from pymongo.write_concern import WriteConcern
from labs.shared.replication import ready,wait_members
from labs.shared.core import timed

def main(run):
    client=ready();wait_members(client);db=client.college_ch09;n=run.count(1000,100)
    for w in [1,'majority',3]:
        for journal in [False,True]:
            col=db[f'w_{w}_{journal}'];col.drop()
            target=col.with_options(write_concern=WriteConcern(w=w,j=journal,wtimeout=5000))
            def writes():
                for i in range(n):target.insert_one({'_id':i,'payload':'same input'})
            _,seconds=timed(writes)
            run.emit('write_latency',w=w,journal=journal,actual_count=n,total_seconds=seconds,average_ms=seconds*1000/n)
    run.emit('partition_activity',command='./scripts/partition.sh',note='Runs host Docker network isolation with automatic reconnect; separate from latency run.')
