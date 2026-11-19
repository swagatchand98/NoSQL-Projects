import time
from labs.shared.core import connect

def ready(timeout=90):
    deadline=time.monotonic()+timeout
    while True:
        try:
            client=connect();client.admin.command('hello')
            if client.primary:return client
        except ModuleNotFoundError:
            raise
        except Exception:
            if time.monotonic()>deadline:raise
        time.sleep(2)


def wait_members(client, count=3, timeout=90):
    deadline=time.monotonic()+timeout
    while time.monotonic()<deadline:
        status=client.admin.command('replSetGetStatus')
        if len([m for m in status['members'] if m['health']==1 and m['stateStr'] in ('PRIMARY','SECONDARY')])==count:return status
        time.sleep(1)
    raise TimeoutError('Replica set did not become healthy')
