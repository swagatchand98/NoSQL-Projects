from pathlib import Path
import time
from pymongo import MongoClient

def credentials():return Path('/input/password').read_text().strip()

def authenticated(user='admin',password=None,auth_source='admin',host='mongo'):
    return MongoClient(host,username=user,password=password or credentials(),authSource=auth_source,tls=True,tlsCAFile='/input/ca.crt',tlsCertificateKeyFile='/input/client.pem',serverSelectionTimeoutMS=5000)

def admin_ready(host='mongo'):
    client=authenticated(host=host)
    for attempt in range(30):
        try:client.admin.command('ping');return client
        except Exception:
            if attempt==29:raise
            time.sleep(2)
