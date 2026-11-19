"""Attributed public records. No generated filler is counted as intelligence."""
import json,time
from urllib.parse import urlparse
from datetime import datetime,timedelta,timezone
from pathlib import Path
import httpx


def normalize(cve,source,published,text,targets=None):
    return dict(_id=cve,source=urlparse(source).netloc,sources=[source],published=published[:10],type='vulnerability',summary=text,targets=targets or ['unspecified'],synthetic=False)


def collect(run):
    if run.mode=='quick':
        records=json.loads(Path('data/threats.json').read_text())
        distinct={r['_id'].rsplit('-',1)[0]:r for r in records}
        rows=[normalize(cve,r['source'],r['source_date'],r['summary'],[r['package']]) for cve,r in distinct.items()]
        run.emit('offline_rehearsal',actual_count=len(rows),note='Historical bundled advisories, not a recent full dataset')
        return rows
    cache=Path('data/public-threats.json')
    if cache.exists():
        rows=json.loads(cache.read_text());run.emit('cached_public_data',actual_count=len(rows));return rows
    records={}
    kev='https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json'
    with httpx.Client(timeout=60,follow_redirects=True) as client:
        response=client.get(kev);response.raise_for_status()
        for v in response.json()['vulnerabilities']:
            records[v['cveID']]=normalize(v['cveID'],kev,v['dateAdded'],v['shortDescription'],[v['product']])
            records[v['cveID']]['date_semantics']='CISA catalog dateAdded, not original advisory publication'
        # NVD publication windows comply with the API maximum date range. Public rate limit respected.
        end=datetime.now(timezone.utc);earliest=end-timedelta(days=1095)
        while len(records)<100000 and end>earliest:
            start=max(earliest,end-timedelta(days=119));offset=0
            while True:
                time.sleep(6.5)
                response=client.get('https://services.nvd.nist.gov/rest/json/cves/2.0',params={'pubStartDate':start.strftime('%Y-%m-%dT%H:%M:%S.000'),'pubEndDate':end.strftime('%Y-%m-%dT%H:%M:%S.000'),'startIndex':offset,'resultsPerPage':2000})
                response.raise_for_status();data=response.json()
                for wrapper in data['vulnerabilities']:
                    c=wrapper['cve'];text=next((d['value'] for d in c['descriptions'] if d['lang']=='en'),'')
                    source='https://nvd.nist.gov/vuln/detail/'+c['id']
                    row=normalize(c['id'],source,c['published'],text,cpe_targets(c.get('configurations',[])))
                    if c['id'] in records:row['sources']=sorted(set(records[c['id']]['sources']+[source]));row['targets']=records[c['id']]['targets']
                    records[c['id']]=row
                offset+=data['resultsPerPage']
                run.emit('ingest_progress',actual_count=len(records),window_start=str(start),window_end=str(end))
                if offset>=data['totalResults'] or len(records)>=100000:break
            end=start-timedelta(milliseconds=1)
    rows=list(records.values())[:100000]
    for row in rows:row['retrieved_at']=datetime.now(timezone.utc).isoformat()
    cache.write_text(json.dumps(rows))
    run.emit('public_ingestion',actual_count=len(rows),target=100000,shortfall=max(0,100000-len(rows)),recent_definition='NVD publications within preceding 1095 days; CISA catalog includes older advisories and is labeled separately')
    return rows


def cpe_targets(value):
    targets=set()
    def visit(node):
        if isinstance(node,dict):
            if node.get('vulnerable') and isinstance(node.get('criteria'),str):
                fields=node['criteria'].split(':')
                if len(fields)>4:targets.add(fields[3]+':'+fields[4])
            for child in node.values():visit(child)
        elif isinstance(node,list):
            for child in node:visit(child)
    visit(value)
    return sorted(targets) or ['unspecified']
