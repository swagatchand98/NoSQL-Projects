import time,uuid
from pymongo import MongoClient
from pymongo.errors import AutoReconnect
from pymongo.write_concern import WriteConcern
from labs.shared.replication import ready,wait_members

def main(run):
    client=ready();status=wait_members(client);run.emit('baseline',members=status['members'])
    marker=str(uuid.uuid4());col=client.college_ch08.probe.with_options(write_concern=WriteConcern(w=3,wtimeout=10000))
    col.insert_one({'_id':marker})
    for member in status['members']:
        with MongoClient('mongodb://'+member['name']+'/?directConnection=true',readPreference='secondaryPreferred',serverSelectionTimeoutMS=5000) as direct:
            assert direct.college_ch08.probe.find_one({'_id':marker})
            run.emit('replication_verified',member=member['name'],role=member['stateStr'])
    if run.activity=='1':return
    config=client.admin.command('replSetGetConfig')['config'];original=[dict(m) for m in config['members']]
    try:
        primary=client.primary
        # Prefer the other secondary, record a prediction rather than assert election outcome.
        candidate=next(m for m in config['members'] if m['host']!=f'{primary[0]}:{primary[1]}')
        for m in config['members']:m['priority']=3 if m['_id']==candidate['_id'] else 1
        config['version']+=1;client.admin.command('replSetReconfig',config)
        run.emit('prediction',preferred=candidate['host'],reason='Higher election priority; availability and timing still matter')
        try:client.admin.command('replSetStepDown',15,secondaryCatchUpPeriodSecs=10)
        except AutoReconnect:pass
        stop=time.monotonic()+35
        while time.monotonic()<stop:
            try:run.emit('observed_member',primary=client.primary,hello=client.admin.command('hello').get('primary'))
            except Exception as exc:run.emit('failover_error',type=type(exc).__name__)
            time.sleep(2)
        run.emit('after_failover',members=wait_members(client)['members'])
    finally:
        config=client.admin.command('replSetGetConfig')['config'];config['members']=original;config['version']+=1
        client.admin.command('replSetReconfig',config)
