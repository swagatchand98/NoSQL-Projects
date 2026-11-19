from labs.shared.core import database, reset

PRODUCTS = [('Redis','Key-Value'),('MongoDB','Document'),('Apache Cassandra','Wide-Column'),('Neo4j','Graph'),('Elasticsearch','Search/Document'),('DynamoDB','Key-Value/Document'),('InfluxDB','Time-Series'),('OrientDB','Multi-Model'),('CouchDB','Document'),('HBase','Wide-Column')]
MAPPINGS = [('Ride-Sharing','profiles','Document','Nested preferences read together'),('Ride-Sharing','ride_history','Wide-Column','Append and time-range queries'),('Ride-Sharing','tracking','Key-Value','Latest positions with TTL'),('Ride-Sharing','payments','Document','Transactional updates'),('Social Media','feed','Document','Flexible content'),('Social Media','social_graph','Graph','Multi-hop relationships'),('Social Media','sentiment','Wide-Column','Time series'),('Social Media','media','Object storage','Large binary objects')]

def main(run):
    db = database(run)
    if run.wants(1):
        col = reset(db, 'products', [dict(name=n, family=f) for n,f in PRODUCTS])
        run.emit('1.1', actual_count=col.count_documents({}), grouped=list(col.aggregate([{'$group':{'_id':'$family','products':{'$push':'$name'}}}])))
    if run.wants(2):
        col = reset(db, 'mapping', [dict(app=a, domain=d, family=f, rationale=r) for a,d,f,r in MAPPINGS])
        run.emit('1.2', actual_count=col.count_documents({}), mappings=list(col.find()))
    run.emit('rubric_gap', activities=['extension_1','extension_2'], reason='Not identified in pinned faculty chapter materials; not claimed complete')
