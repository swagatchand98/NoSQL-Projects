import os,time
from labs.shared.auth import authenticated
from labs.shared.core import Blocked

def main(run):
    client=authenticated(host='mongo1')
    # The secure bootstrap is performed by scripts/secure-replica.sh using localhost exception.
    status=client.admin.command('replSetGetStatus')
    assert len([m for m in status['members'] if m['health']==1])==3
    run.emit('authenticated_members',members=status['members'])
    from pymongo import MongoClient
    from labs.shared.auth import credentials
    driver=MongoClient('mongodb://mongo1,mongo2,mongo3/?replicaSet=secure',username='admin',password=credentials(),tls=True,tlsCAFile='/input/ca.crt',serverSelectionTimeoutMS=5000)
    try:driver.admin.command('replSetStepDown',10)
    except Exception:pass
    for i in range(15):
        try:run.emit('client_failover',primary=driver.admin.command('hello').get('primary'))
        except Exception as exc:run.emit('election_in_progress',type=type(exc).__name__)
        time.sleep(2)
    from labs.shared.auth import credentials
    from pymongo.errors import OperationFailure
    try:driver.admin.command('createUser','exporter',pwd=credentials(),roles=[{'role':'clusterMonitor','db':'admin'},{'role':'read','db':'local'}])
    except OperationFailure as exc:
        if exc.code!=51003:raise
    run.emit('exporter',command='./scripts/exporter.sh')
    run.emit('external_check_blocked',check='Kubernetes persistence/rejoin',reason='Must run ./scripts/kubernetes.sh on a configured cluster')
    run.emit('kubernetes',command='./scripts/kubernetes.sh',note='Separate external verification; not inferred from Compose results')
