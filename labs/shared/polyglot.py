import os,time
from cassandra.cluster import Cluster, NoHostAvailable
from neo4j import GraphDatabase,Query
from neo4j.exceptions import ServiceUnavailable, SessionExpired
from labs.shared.readiness import connect_fresh
from labs.shared.core import connect

class Backends:
    def __init__(self):
        deadline=time.monotonic()+90
        while True:
            try:self.mongo=connect();break
            except ModuleNotFoundError:
                raise
            except Exception:
                if time.monotonic()>deadline:raise
                time.sleep(2)
        try:
            self.cluster, self.cassandra = connect_fresh(
                lambda: Cluster([os.getenv('CASSANDRA_HOST', 'localhost')], connect_timeout=5),
                lambda cluster: cluster.connect(), lambda cluster: cluster.shutdown(),
                timeout=150, retry_errors=(NoHostAvailable,))
        except Exception:
            self.mongo.close()
            raise
        self.cassandra.default_timeout=15
        self.cassandra.execute("CREATE KEYSPACE IF NOT EXISTS college WITH replication = {'class':'SimpleStrategy','replication_factor':1}")
        self.cassandra.set_keyspace('college')
        try:
            self.graph, _ = connect_fresh(
                lambda: GraphDatabase.driver(os.getenv('NEO4J_URI', 'bolt://localhost:7687'),
                                             auth=None, connection_timeout=5),
                lambda graph: graph.verify_connectivity(), lambda graph: graph.close(),
                timeout=150, retry_errors=(ServiceUnavailable, SessionExpired))
        except Exception:
            self.mongo.close()
            self.cluster.shutdown()
            raise

    def cypher(self,query,**params):
        with self.graph.session() as session:return [r.data() for r in session.run(Query(query,timeout=30),**params)]

    def close(self):
        self.mongo.close();self.cluster.shutdown();self.graph.close()
