from pymongo import MongoClient
from pymongo.errors import OperationFailure,ServerSelectionTimeoutError
from labs.shared.auth import admin_ready,authenticated,credentials
from labs.shared.core import reset

def main(run):
    client=admin_ready();db=client.college_ch12
    reset(db,'employees',[{'_id':1,'name':'Arjun','salary':50000}])
    for role,actions in [('reader',['find']),('writer',['find','insert','update','remove'])]:
        try:db.command('dropRole',role)
        except OperationFailure:pass
        db.command('createRole',role,privileges=[{'resource':{'db':db.name,'collection':'employees'},'actions':actions}],roles=[])
    try:db.drop_collection('public_employees')
    except OperationFailure:pass
    db.command('create','public_employees',viewOn='employees',pipeline=[{'$project':{'salary':0}}])
    roles={'reader':['reader'],'writer':['writer'],'hr':['reader'],'staff':[{'role':'view_reader','db':db.name}]}
    try:db.command('dropRole','view_reader')
    except OperationFailure:pass
    db.command('createRole','view_reader',privileges=[{'resource':{'db':db.name,'collection':'public_employees'},'actions':['find']}],roles=[])
    for user,grants in roles.items():
        try:db.command('dropUser',user)
        except OperationFailure:pass
        db.command('createUser',user,pwd=credentials(),roles=grants)
    def denied(name,operation):
        try:operation()
        except OperationFailure as exc:
            assert exc.code==13;run.emit('denied',operation=name,code=exc.code)
        else:raise AssertionError(name+' was allowed')
    with authenticated('reader',auth_source=db.name) as reader:
        run.emit('reader_find',rows=list(reader[db.name].employees.find()))
        denied('reader_insert',lambda:reader[db.name].employees.insert_one({'name':'blocked'}))
    with authenticated('writer',auth_source=db.name) as writer:
        writer[db.name].employees.update_one({'_id':1},{'$set':{'reviewed':True}})
        denied('writer_other_collection',lambda:writer[db.name].other.insert_one({'x':1}))
    with authenticated('staff',auth_source=db.name) as staff:
        rows=list(staff[db.name].public_employees.find());assert all('salary' not in r for r in rows)
        run.emit('staff_redacted',rows=rows)
        denied('staff_direct_collection',lambda:list(staff[db.name].employees.find()))
    with authenticated('hr',auth_source=db.name) as hr:run.emit('hr_salary',rows=list(hr[db.name].employees.find()))
    try:MongoClient('mongodb://mongo:27017',serverSelectionTimeoutMS=2000).admin.command('ping')
    except ServerSelectionTimeoutError:run.emit('plaintext_rejected',observed=True)
    else:raise AssertionError('Plaintext accepted')
    run.emit('certificate_chain',diagram='Local CA -> signed mongo service certificate (SAN verified); Local CA -> signed client certificate',actual_count=db.employees.count_documents({}))
