import os
from labs.shared.core import database, reset, seed_data, connect

def main(run):
    db = database(run)
    run.emit('docker_server_info', info=db.client.server_info())
    if os.getenv('MONGO_URI_ATLAS'):
        with connect(os.environ['MONGO_URI_ATLAS']) as client:
            run.emit('atlas_server_info', info=client.server_info())
    else:
        run.emit('external_check_blocked', check='Atlas server_info', reason='MONGO_URI_ATLAS absent')
    if run.activity in ('1','3'):return
    col = reset(db, 'books', seed_data('books'))
    for name,query in [('recent',{'year':{'$gt':2020}}),('genre',{'genre':'Machine Learning'}),('price',{'price':{'$gte':40,'$lte':60}}),('array',{'tags':'AI'})]:
        run.emit(name, rows=list(col.find(query)))
    before = list(col.find({'year':{'$lt':2010}}))
    result = col.update_many({'year':{'$lt':2010}}, [{'$set':{'price':{'$round':[{'$multiply':['$price',1.1]},2]}}}])
    run.emit('price_update', before=before, after=list(col.find({'year':{'$lt':2010}})), modified=result.modified_count, compass_filter={'year':{'$lt':2010}})
    col.insert_one({'_id':'delete-demo','title':'Temporary CRUD book'})
    assert col.delete_one({'_id':'delete-demo'}).deleted_count == 1
    run.emit('crud_complete', actual_count=col.count_documents({}))
