from labs.shared.core import database, reset, seed_data

def main(run):
    db=database(run);docs=seed_data('orders')
    docs += [dict(order_id=f'BOUND-{i}',customer=['Arjun','Sneha','Kavya'][i%3],status=['completed','pending','cancelled'][i%3],total=[49,50,200,201][i%4],items=1,date='2024-04-10',region='North') for i in range(10)]
    for i,d in enumerate(docs):d['product_ids']=[i%4]
    orders=reset(db,'orders',docs);products=reset(db,'products',[dict(_id=i,name=f'Product {i}',active=i%2==0) for i in range(5)])
    pipelines={'monthly':[{'$match':{'status':'completed'}},{'$group':{'_id':{'$substrBytes':['$date',0,7]},'revenue':{'$sum':'$total'}}},{'$sort':{'_id':1}}],
    'top_three':[{'$match':{'status':'completed'}},{'$group':{'_id':'$customer','total':{'$sum':'$total'},'product_sets':{'$push':'$product_ids'}}},{'$sort':{'total':-1,'_id':1}},{'$limit':3},{'$set':{'product_ids':{'$reduce':{'input':'$product_sets','initialValue':[],'in':{'$setUnion':['$$value','$$this']}}}}},{'$lookup':{'from':'products','localField':'product_ids','foreignField':'_id','as':'products'}}],
    'average':[{'$group':{'_id':'$status','average':{'$avg':'$total'}}}],
    'buckets':[{'$group':{'_id':{'$switch':{'branches':[{'case':{'$lt':['$total',50]},'then':'below 50'},{'case':{'$lte':['$total',200]},'then':'50 through 200'}],'default':'above 200'}},'count':{'$sum':1}}}],
    'join':[{'$lookup':{'from':'products','localField':'product_ids','foreignField':'_id','as':'products'}}],
    'filtered_join':[{'$lookup':{'from':'products','localField':'product_ids','foreignField':'_id','pipeline':[{'$match':{'active':True}}],'as':'active_products'}}]}
    selected={'1':['monthly','top_three','average','buckets'],'2':['join','filtered_join'],'3':['buckets'],'4':['filtered_join']}
    for name,p in pipelines.items():
        if run.activity=='all' or name in selected.get(run.activity,[]):run.emit(name,rows=list(orders.aggregate(p)))
    never=list(products.aggregate([{'$lookup':{'from':'orders','localField':'_id','foreignField':'product_ids','as':'orders'}},{'$match':{'orders':{'$size':0}}}]))
    assert [d['_id'] for d in never]==[4]
    run.emit('never_ordered',rows=never,actual_count=orders.count_documents({}))
