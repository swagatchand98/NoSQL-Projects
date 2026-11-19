from datetime import datetime,timedelta
from bson import MinKey,MaxKey
from labs.shared.core import database,explain

def main(run):
    db=database(run);admin=db.client.admin
    matrix=[dict(key='order_id',cardinality='high',distribution='monotonic risk',equality='targeted',range='targeted'),dict(key='customer_id',cardinality='customers',distribution='hot customer risk',equality='targeted',range='targeted'),dict(key='order_date',cardinality='timestamp precision',distribution='monotonic hotspot',equality='targeted',range='targeted'),dict(key='hashed customer_id',cardinality='customers',distribution='spread customers; one hot customer remains hot',equality='targeted',range='scatter')]
    run.emit('decision_matrix',rows=matrix,recommendation='Hashed customer_id for equality customer-scoped lookups; cannot split a single hot customer by hashing alone.')
    assert admin.command('hello').get('msg')=='isdbgrid','A real mongos is required'
    db.client.drop_database(db.name)
    admin.command('enableSharding',db.name,primaryShard='s1')
    admin.command('balancerStop')
    try:
        db.create_collection('monotonic');db.monotonic.create_index('ts');admin.command('shardCollection',db.name+'.monotonic',key={'ts':1})
        boundary=datetime(2024,1,1)
        admin.command('split',db.name+'.monotonic',middle={'ts':boundary})
        admin.command('moveChunk',db.name+'.monotonic',find={'ts':boundary-timedelta(days=1)},to='s2')
        db.create_collection('hashed');db.hashed.create_index([('customer_id','hashed')]);admin.command('shardCollection',db.name+'.hashed',key={'customer_id':'hashed'},numInitialChunks=4)
        metadata=db.client.config.collections.find_one({'_id':db.name+'.hashed'})
        chunks=list(db.client.config.chunks.find({'uuid':metadata['uuid']}).sort('min',1))
        for i,chunk in enumerate(chunks):
            admin.command('moveChunk',db.name+'.hashed',bounds=[chunk['min'],chunk['max']],to='s1' if i%2==0 else 's2')
        run.emit('prepared_hashed_ranges',chunks=list(db.client.config.chunks.find({'uuid':metadata['uuid']})))
        n=run.count(10000)
        docs=[dict(_id=i,ts=boundary+timedelta(seconds=i),customer_id=f'C{i%1000}',payload='x'*100) for i in range(n)]
        for name in ['monotonic','hashed']:
            col=db[name];col.insert_many([dict(d) for d in docs])
            stats=db.command('collStats',name)
            run.emit('distribution',collection=name,actual_count=n,shards=stats.get('shards',{}));run.save(name+'-stats.json',stats)
            result=explain(col,{'ts':{'$gte':boundary,'$lt':boundary+timedelta(seconds=100)}})
            run.save(name+'-timestamp.json',result)
            run.emit('query_shards',collection=name,shards=shard_names(result))
        for name,q in [('equality',{'customer_id':'C42'}),('range',{'customer_id':{'$gte':'C10','$lt':'C20'}})]:
            result=explain(db.hashed,q);run.save('hashed-'+name+'.json',result);run.emit('hashed_targeting',query=name,shards=shard_names(result))
    finally:admin.command('balancerStart')


def shard_names(value):
    names=set()
    if isinstance(value,dict):
        if isinstance(value.get("shardName"),str):names.add(value["shardName"])
        for child in value.values():names.update(shard_names(child))
    elif isinstance(value,list):
        for child in value:names.update(shard_names(child))
    return sorted(names)
