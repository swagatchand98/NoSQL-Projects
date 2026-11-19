"""Dependency-injected pooled clients and independent circuit breakers."""
import time

class CircuitOpen(RuntimeError):pass

class CircuitBreaker:
    def __init__(self,threshold=3,cooldown=10):
        self.threshold=threshold;self.cooldown=cooldown;self.failures=0;self.opened=0
    def call(self,operation):
        if self.failures>=self.threshold and time.monotonic()-self.opened<self.cooldown:raise CircuitOpen('Backend cooling down')
        try:result=operation()
        except Exception:
            self.failures+=1;self.opened=time.monotonic();raise
        self.failures=0;return result

class FraudQueryService:
    def __init__(self,mongo,cassandra,graph):
        self.mongo=mongo;self.cassandra=cassandra;self.graph=graph
        self.breakers={name:CircuitBreaker() for name in ['mongo','cassandra','neo4j']}
    def get_transaction(self,transaction_id):
        return self.breakers['mongo'].call(lambda:self.mongo.transactions.find_one({'_id':transaction_id}))
    def get_user_profile(self,user_id):
        return self.breakers['cassandra'].call(lambda:self.cassandra.execute('SELECT * FROM profiles WHERE user_id=%s',(user_id,)).one())
    def detect_fraud_rings(self,user_id,max_depth=3,limit=20):
        if not 2<=max_depth<=4 or not 1<=limit<=100:raise ValueError('Traversal bounds exceeded')
        # Only the validated integer depth is interpolated. All data remains parameters.
        query=f'MATCH p=(u:LabUser {{id:$id}})-[:SHARES_DEVICE*2..{max_depth}]-(u) UNWIND nodes(p) AS v WITH DISTINCT u,v WHERE v.id <> u.id RETURN v.id AS id LIMIT $limit'
        return self.breakers['neo4j'].call(lambda:self.graph(query,id=user_id,limit=limit))
    def investigate(self,transaction_id):
        tx=self.get_transaction(transaction_id)
        if not tx:return None
        return {'transaction':tx,'profile':self.get_user_profile(tx['user_id']),'ring_candidates':self.detect_fraud_rings(tx['user_id']),'classification':'Candidates require analyst verification, not confirmed fraud'}
