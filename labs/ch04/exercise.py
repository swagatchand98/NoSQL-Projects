from labs.shared.core import database, reset, seed_data

def main(run):
    from pymongo import UpdateOne
    db=database(run);docs=seed_data('products')+seed_data('inventory')
    docs += [dict(sku=f'EXT-{i}',name=f'Extra product {i}',price=20+i,stock=i,category='Accessories',tags=['wireless'],rating=4,active=True) for i in range(3)]
    validator={'$jsonSchema':{'bsonType':'object','required':['sku','name','price','stock'],'properties':{'sku':{'bsonType':'string'},'name':{'bsonType':'string'},'price':{'bsonType':['int','double','decimal'],'minimum':0},'stock':{'bsonType':'int','minimum':0}}}}
    col=reset(db,'inventory',docs,validator);col.create_index('sku',unique=True)
    queries={'price':{'price':{'$gte':500,'$lte':800}},'stock':{'stock':{'$gt':10}},'or':{'$or':[{'category':'Laptops'},{'category':'Monitors'}]},'and':{'$and':[{'stock':{'$gt':10}},{'rating':{'$gte':4.5}}]},'membership':{'tags':'mechanical'},'all':{'tags':{'$all':['mechanical','wireless']}},'substring':{'name':{'$regex':'book','$options':'i'}}}
    if run.wants(1,3):
        for name,q in queries.items():run.emit(name,rows=list(col.find(q)))
        run.emit('pages',pages=[list(col.find().sort([('name',1),('sku',1)]).skip(i*3).limit(3)) for i in range(4)])
    if run.wants(2):
        col.insert_one(dict(sku='TEMP',name='Temporary',price=1,stock=1));col.update_one({'sku':'TEMP'},{'$set':{'price':2}});assert col.delete_one({'sku':'TEMP'}).deleted_count==1
        for sku,fields in [('WGT-001',{'price':279.99,'stock':45}),('WGT-003',{'name':'SmartRing X','price':199.99,'stock':100})]:
            result=col.update_one({'sku':sku},{'$set':fields,'$setOnInsert':{'sku':sku}},upsert=True)
            run.emit('sku_upsert',sku=sku,matched=result.matched_count,modified=result.modified_count,upserted_id=result.upserted_id)
        operations=[UpdateOne({'sku':'WGT-001'},{'$inc':{'stock':-10}}),UpdateOne({'sku':'WGT-002'},{'$mul':{'price':.9}}),UpdateOne({'sku':'WGT-003'},{'$set':{'active':True}}),UpdateOne({'sku':'WGT-004'},{'$set':{'name':'EarBuds Ultra','price':79.99,'stock':150}},upsert=True),UpdateOne({'sku':'MON-001'},{'$set':{'reviewed':True}})]
        result=col.bulk_write(operations)
        run.emit('bulk',modified=result.modified_count,upserted=result.upserted_count,fifth_operation='Provisional reviewed flag: faculty source contains only four operations')
    if run.wants(4):
        imports=[UpdateOne({'sku':d['sku']},{'$set':d},upsert=True) for d in docs]
        col.bulk_write(imports);count=col.count_documents({});second=col.bulk_write(imports)
        assert col.count_documents({})==count and second.upserted_count==0
        run.emit('second_import',actual_count=count,modified=second.modified_count,upserted=second.upserted_count)
