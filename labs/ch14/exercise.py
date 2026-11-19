import hashlib,json,os,subprocess,time
from datetime import datetime,timezone,timedelta
from pathlib import Path
from labs.shared.core import reset,timed
from labs.shared.replication import ready

def checksum(col):
    return hashlib.sha256(json.dumps(list(col.find().sort('_id')),default=str,sort_keys=True).encode()).hexdigest()

def main(run):
    client=ready();db=client.college_ch14
    for tool in ['mongodump','mongorestore']:
        run.emit('tool_version',tool=tool,output=subprocess.run([tool,'--version'],check=True,capture_output=True,text=True).stdout)
    run.emit('server_version',version=client.server_info()['version'])
    for i in range(3 if run.mode=='full' else 2):
        status=client.admin.command('serverStatus');rs=client.admin.command('replSetGetStatus')
        cache=status.get('wiredTiger',{}).get('cache',{});requests=cache.get('pages requested from the cache',0)
        ratio=max(0,1-cache.get('pages read into cache',0)/requests) if requests else None
        primary=next(m for m in rs['members'] if m['stateStr']=='PRIMARY')
        lag=max([max(0,(primary['optimeDate']-m['optimeDate']).total_seconds()) for m in rs['members'] if m['stateStr']=='SECONDARY'] or [0])
        warnings=[]
        if ratio is not None and ratio<.8:warnings.append('Estimated cache hit ratio below 80%')
        if lag>10:warnings.append('Replication lag above 10 seconds')
        run.emit('monitor',connections=status['connections'],opcounters=status['opcounters'],cache=cache,estimated_hit_ratio=ratio,replication_lag_seconds=lag,warnings=warnings)
        if warnings and os.getenv('MONITOR_WEBHOOK'):
            import httpx
            httpx.post(os.environ['MONITOR_WEBHOOK'],json={'warnings':warnings},timeout=5).raise_for_status()
        if i==0:time.sleep(30)
    backup_root=Path('/work/backups/ch14');backup_root.mkdir(parents=True,exist_ok=True)
    for old in backup_root.glob('snapshot-*.archive'):
        if datetime.fromtimestamp(old.stat().st_mtime,timezone.utc)<datetime.now(timezone.utc)-timedelta(days=7):old.unlink()
    for n in ([1000,10000,100000] if run.mode=='full' else [1000]):
        col=reset(db,'restore_test',[{'_id':i,'value':'original'} for i in range(n)]);before=checksum(col)
        archive=backup_root/f'snapshot-{datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")}-{n}.archive'
        uri=os.environ['MONGO_URI']
        subprocess.run(['mongodump','--uri',uri,'--db',db.name,'--archive='+str(archive)],check=True,capture_output=True)
        col.update_many({},{'$set':{'value':'modified'}})
        target=client.college_ch14_restored;target.drop_collection('restore_test')
        _,seconds=timed(lambda:subprocess.run(['mongorestore','--uri',uri,'--archive='+str(archive),'--nsFrom',db.name+'.*','--nsTo',target.name+'.*'],check=True,capture_output=True))
        assert target.restore_test.count_documents({})==n and checksum(target.restore_test)==before
        run.emit('snapshot_restore',actual_count=n,seconds=seconds,checksum=before)
    run.emit('pitr',command='./scripts/pitr.sh',note='Separate full replica-set dump and oplog timestamp restore; scheduled snapshots alone are not PITR.')
