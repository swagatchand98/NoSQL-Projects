"""Controlled timestamp replay on an isolated MongoDB target.
Requires PITR_TARGET_URI; never restore over the source replica set.
"""
import os,subprocess,time
from pathlib import Path
from bson import BSON
from labs.shared.core import connect,Run,Blocked

def main():
    run=Run('ch14','full','pitr')
    try:
        source=os.environ['MONGO_URI'];target=os.getenv('PITR_TARGET_URI')
        if not target or target==source:raise Blocked('Set PITR_TARGET_URI to an isolated, disposable matching-version replica set')
        client=connect(source);dest=connect(target)
        assert client.server_info()['version']==dest.server_info()['version']
        probe=client.college_ch14_pitr.probe;probe.drop();probe.insert_one({'_id':1,'value':'base'})
        directory=run.directory/'dump'
        subprocess.run(['mongodump','--uri',source,'--oplog','--out',str(directory)],check=True,capture_output=True)
        # Capture the complete post-backup oplog interval. This controlled exercise has no concurrent writers.
        start=client.local.oplog.rs.find_one(sort=[('$natural',-1)])['ts']
        probe.update_one({'_id':1},{'$set':{'value':'wanted'}})
        cutoff=client.local.oplog.rs.find_one(sort=[('$natural',-1)])['ts']
        probe.update_one({'_id':1},{'$set':{'value':'unwanted'}})
        end=client.local.oplog.rs.find_one(sort=[('$natural',-1)])['ts']
        with (directory/'oplog.bson').open('ab') as stream:
            for entry in client.local.oplog.rs.find({'ts':{'$gt':start,'$lte':end}}).sort('$natural',1):stream.write(BSON.encode(entry))
        subprocess.run(['mongorestore','--uri',target,'--drop','--oplogReplay','--oplogLimit',f'{end.time}:{end.inc}',str(directory)],check=True,capture_output=True)
        observed=dest.college_ch14_pitr.probe.find_one({'_id':1});assert observed['value']=='wanted'
        run.emit('timestamp_restore',cutoff_exclusive=str(end),wanted_timestamp=str(cutoff),observed=observed,actual_count=1)
        run.finish('passed')
    except Exception as exc:
        run.finish('blocked' if isinstance(exc,Blocked) else 'failed',type(exc).__name__);raise
if __name__=='__main__':main()
