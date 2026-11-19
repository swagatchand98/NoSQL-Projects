import json,statistics,time
from datetime import datetime,timedelta,timezone
from labs.shared.core import reset,timed
from labs.shared.polyglot import Backends
from labs.ch18.ingest import collect

def main(run):
    records=collect(run)
    if not records:raise ValueError('No attributable threat records')
    back=Backends()
    try:
        db=back.mongo.college_ch18
        full=reset(db,'full_history',records)
        reset(db,'load_test')
        cutoff=(datetime.now(timezone.utc)-timedelta(days=90)).date().isoformat()
        recent=reset(db,'recent',[r for r in records if r['published']>=cutoff])
        full.create_index([('source',1),('published',1)]);full.create_index('targets')
        cs=back.cassandra
        for table,partition in [('threat_by_source','source'),('threat_by_type','kind'),('threat_by_target','target')]:
            cs.execute(f'DROP TABLE IF EXISTS {table}')
            cs.execute(f'CREATE TABLE {table} (source text,kind text,target text,published text,id text,summary text,PRIMARY KEY ({partition},published,id))')
        statements={table:cs.prepare(f'INSERT INTO {table} (source,kind,target,published,id,summary) VALUES (?,?,?,?,?,?)') for table in ['threat_by_source','threat_by_type','threat_by_target']}
        back.cypher('MATCH(n) WHERE n:LabThreat OR n:LabSource OR n:LabTarget DETACH DELETE n')
        back.cypher('CREATE CONSTRAINT lab_threat_id IF NOT EXISTS FOR (n:LabThreat) REQUIRE n.id IS UNIQUE')
        def insert_cassandra(rows):
            for r in rows:
                args=(r['source'],r['type'],r['targets'][0],r['published'],r['_id'],r['summary'])
                for table in ['threat_by_source','threat_by_type']:cs.execute(statements[table],args)
                for target in r['targets']:cs.execute(statements['threat_by_target'],(r['source'],r['type'],target,r['published'],r['_id'],r['summary']))
        def insert_graph(rows):
            for start in range(0,len(rows),500):back.cypher('UNWIND $rows AS r MERGE(t:LabThreat {id:r._id}) SET t.published=r.published,t.kind=r.type,t.summary=r.summary WITH t,r,r.source AS source MERGE(s:LabSource {url:source}) MERGE(s)-[:REPORTS]->(t) WITH DISTINCT t,r UNWIND r.targets AS target MERGE(x:LabTarget {name:target}) MERGE(t)-[:AFFECTS]->(x)',rows=rows[start:start+500])
        insert_cassandra(records);insert_graph(records)
        source=records[0]['source'];target=records[0]['targets'][0]
        operations={
          'MongoDB':{'history':lambda:list(full.find({'source':source}).sort('published',1)), 'target_spread':lambda:list(full.find({'targets':target})), 'daily_volume':lambda:list(full.aggregate([{'$group':{'_id':'$published','count':{'$sum':1}}}]))},
          'Cassandra':{'history':lambda:list(cs.execute('SELECT * FROM threat_by_source WHERE source=%s',(source,))), 'target_spread':lambda:list(cs.execute('SELECT * FROM threat_by_target WHERE target=%s',(target,))), 'daily_volume':lambda:daily(cs.execute('SELECT published FROM threat_by_type WHERE kind=%s',('vulnerability',)))},
          'Neo4j':{'history':lambda:back.cypher('MATCH(:LabSource {url:$source})-[:REPORTS]->(t:LabThreat) RETURN t ORDER BY t.published',source=source), 'target_spread':lambda:back.cypher('MATCH(t:LabThreat)-[:AFFECTS]->(:LabTarget {name:$target}) RETURN t',target=target), 'daily_volume':lambda:back.cypher('MATCH(t:LabThreat) RETURN t.published AS day,count(*) AS count')}
        }
        measurements=[]
        for backend,queries in operations.items():
            for name,operation in queries.items():
                times=[]
                for repeat in range(10):
                    value,seconds=timed(operation);times.append(seconds)
                row=dict(backend=backend,operation=name,actual_count=len(records),runs=10,median_seconds=statistics.median(times),samples_seconds=times)
                measurements.append(row);run.emit('benchmark',**row)
        # Throughput uses distinct, labeled generated load rows; they are removed from report collections afterward.
        for backend in operations:
            times=[];batch_size=run.count(1000,30)
            for repeat in range(10):
                batch=[dict(_id=f'LOAD-{repeat}-{i}',source='generated-load',sources=['generated-load'],type='load-test',targets=['synthetic'],published='2024-01-01',summary='Generated benchmark record; not a report',synthetic=True) for i in range(batch_size)]
                operation={'MongoDB':lambda:db.load_test.insert_many([dict(r) for r in batch]),'Cassandra':lambda:insert_cassandra(batch),'Neo4j':lambda:insert_graph(batch)}[backend]
                _,seconds=timed(operation);times.append(seconds)
            row=dict(backend=backend,operation='insert_throughput',actual_count=batch_size,runs=10,median_records_per_second=batch_size/statistics.median(times),samples_seconds=times,synthetic=True)
            measurements.append(row);run.emit('benchmark',**row)
        candidates=back.cypher('MATCH(t:LabThreat)-[:AFFECTS]->(x:LabTarget) WHERE x.name <> "synthetic" AND x.name <> "unspecified" WITH x,collect(t.id) AS ids WHERE size(ids)>1 RETURN x.name AS target,ids ORDER BY size(ids) DESC LIMIT 10')
        for c in candidates:c['mongo_details']=list(full.find({'_id':{'$in':c['ids'][:10]}}));c['assessment']='Candidate relationship only: shared package/source can create false positives; not confirmed threat coordination.'
        run.emit('interconnected_candidates',candidates=candidates)
        run.save('measurements.json',measurements)
        lines=['# Comparative threat intelligence report', '## Executive summary','Measured results below apply only to this machine and dataset. No universal database winner is asserted.','## Methodology and environment',f'Mode: {run.mode}; attributable records: {len(records)}; recent records: {recent.count_documents({})}. Ten repetitions per workload. Generated insert load is separate from reports.',f'MongoDB version: {back.mongo.server_info()["version"]}. Capture Docker image digests with the launcher.', '## Architecture','```mermaid\nflowchart LR\n Sources-->Ingest\n Ingest-->MongoDB\n Ingest-->Cassandra\n Ingest-->Neo4j\n MongoDB-->Investigation\n Neo4j-->Investigation\n```','## Schema','MongoDB: recent/full documents. Cassandra: tables partitioned by source, type, target. Neo4j: Source REPORTS Threat AFFECTS Target. Target relationships express advisory coverage, not observed propagation.','## Performance',json.dumps(measurements,indent=2),'## Ergonomics and recommendations','Use MongoDB for flexible report details and aggregation; Cassandra for known partition queries; Neo4j for bounded relationship exploration. Cassandra daily aggregation here reads a type partition client-side, exposing its modeling trade-off.','## Scaling estimates',json.dumps(scaling(full,records),indent=2),'These are uncompressed document-byte estimates, excluding indexes, replication, engine overhead and backup copies; not measured 1M/10M/100M benchmarks.','## Backup, monitoring, skills','MongoDB: tested dump/restore exercises and replication monitoring. Cassandra: snapshots plus repair procedures. Neo4j: version/edition-supported backups. Operational skills and recovery testing are needed for each additional engine.','## Findings and limitations',json.dumps(candidates,default=str,indent=2)]
        (run.directory/'comparison.md').write_text('\n\n'.join(lines))
    finally:back.close()

def daily(rows):
    result={}
    for row in rows:result[row.published]=result.get(row.published,0)+1
    return result


def scaling(col,records):
    from bson import BSON
    average=sum(len(BSON.encode(r)) for r in records)/len(records)
    return [{"records":n,"estimated_raw_GiB":n*average/(1024**3),"assumption":"Current sample average BSON bytes per record"} for n in [1000000,10000000,100000000]]
