import os,secrets,time
from datetime import datetime,timezone
from labs.shared.core import database,reset,timed

def main(run):
    import jwt
    from fastapi.testclient import TestClient
    os.environ['JWT_SECRET']=os.getenv('JWT_SECRET') or secrets.token_hex(32)
    from labs.ch15.api import app
    db=database(run)
    docs=[dict(_id=f'{t}-{i}',tenant_id=f'tenant{t}',owner_id=f'user{t}',title=f'Task {i}',status='pending',created_at=datetime(2024,1,1,tzinfo=timezone.utc)) for t in range(5) for i in range(100)]
    source=reset(db,'tasks',docs);source.create_index([('tenant_id',1),('created_at',1)]);reset(db,'rate_limits')
    def token(tenant,user,role='member'):
        return jwt.encode(dict(tenant_id=tenant,sub=user,role=role,exp=int(time.time())+300,iss='college-lab-issuer',aud='college-labs'),os.environ['JWT_SECRET'],algorithm='HS256')
    def headers(tenant,user,role='member'):return {'Authorization':'Bearer '+token(tenant,user,role)}
    with TestClient(app) as http:
        h=headers('tenant0','user0');foreign=headers('tenant1','user1')
        created=http.post('/tasks',headers=h,json={'title':'CRUD test'});assert created.status_code==201
        task_id=created.json()['_id']
        assert http.get('/tasks/'+task_id,headers=h).status_code==200
        for method,payload in [('get',None),('patch',{'title':'attack'}),('delete',None)]:
            response=http.request(method,'/tasks/'+task_id,headers=foreign,**({'json':payload} if payload else {}));assert response.status_code==404
            run.emit('cross_tenant_denied',method=method,status=response.status_code)
        assert http.patch('/tasks/'+task_id,headers=h,json={'title':'changed'}).status_code==200
        assert http.get('/tasks/'+task_id,headers=headers('tenant0','different')).status_code==404
        assert http.get('/tasks/'+task_id,headers=headers('tenant0','admin','tenant-admin')).status_code==200
        assert http.delete('/tasks/'+task_id,headers=h).status_code==204
        assert http.get('/tasks',headers={'Authorization':'Bearer forged'}).status_code==401
        os.environ['RATE_LIMIT']='1';reset(db,'rate_limits')
        assert http.get('/tasks',headers=h).status_code==200
        assert http.get('/tasks',headers=h).status_code==429
        os.environ['RATE_LIMIT']='100'
    for t in range(5):
        tenant=f'tenant{t}';target=reset(db,'tasks_'+tenant)
        target.create_index('created_at')
        for iteration in range(2):
            for doc in source.find({'tenant_id':tenant}):target.replace_one({'_id':doc['_id']},doc,upsert=True)
        assert list(source.find({'tenant_id':tenant}).sort('_id'))==list(target.find().sort('_id'))
        assert target.count_documents({'tenant_id':{'$ne':tenant}})==0
        run.emit('migration',tenant=tenant,actual_count=target.count_documents({}))
    for design in ['shared','collections']:
        col=source if design=='shared' else db.tasks_tenant0
        query={'tenant_id':'tenant0'} if design=='shared' else {}
        _,listing=timed(lambda:list(col.find(query).sort('created_at',1)))
        _,creation=timed(lambda:col.insert_one(dict(_id='benchmark',tenant_id='tenant0',owner_id='user0',title='benchmark',created_at=datetime.now(timezone.utc))))
        col.delete_one({'_id':'benchmark'})
        def analytics():
            if design=='shared':return list(source.aggregate([{'$group':{'_id':'$tenant_id','count':{'$sum':1}}}]))
            return [{'_id':f'tenant{t}','count':db[f'tasks_tenant{t}'].count_documents({})} for t in range(5)]
        result,seconds=timed(analytics)
        run.emit('design_benchmark',design=design,actual_count=500,list_seconds=listing,create_seconds=creation,analytics_seconds=seconds,analytics=result)
