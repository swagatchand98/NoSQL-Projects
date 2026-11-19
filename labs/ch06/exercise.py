from labs.shared.core import database, reset, explain, stages, timed

def main(run):
    from pymongo.errors import OperationFailure
    db=database(run);n=run.count(50000)
    docs=[dict(_id=i,sku=f'SKU-{i}',name=f'Product {i}',category=f'cat{i%10}',price=i%1000,stock=i%50,tags=['wireless' if i%2 else 'wired']) for i in range(n)]
    col=reset(db,'products',docs)
    queries=[{'sku':'SKU-42'},{'category':'cat2','price':{'$gt':200}},{'stock':{'$lt':5}},{'tags':'wireless'},{'$text':{'$search':'Product'}}]
    for phase in ['before','after','retained']:
        if phase=='after':
            for keys in [[('sku',1)],[('category',1),('price',1)],[('stock',1)],[('tags',1)],[('name','text')]]:col.create_index(keys)
        if phase=='retained':
            for name in ['sku_1','stock_1','tags_1','name_text']:col.drop_index(name)
        for i,q in enumerate(queries):
            try:
                list(col.find(q).limit(20))
                result=explain(col,q);run.save(f'{phase}-{i}.json',result)
                run.emit('query_plan',phase=phase,query=i,stages=stages(result),totalDocsExamined=result['executionStats']['totalDocsExamined'])
            except OperationFailure as exc:
                if i!=4:raise
                run.emit('text_index_limitation',phase=phase,code=exc.code)
        run.emit('index_usage',phase=phase,stats=list(col.aggregate([{'$indexStats':{}}])))
    covered=explain(col,{'category':'cat2'},{'_id':0,'category':1,'price':1})
    run.save('covered.json',covered)
    assert covered['executionStats']['totalDocsExamined']==0
    batch=docs[:run.count(10000)]
    timings=[]
    for extra in [0,5]:
        target=reset(db,f'inserts_{extra}')
        if extra:
            for key in ['sku','category','price','stock','name']:target.create_index(key)
        _,seconds=timed(lambda:target.insert_many([dict(d) for d in batch]))
        timings.append(dict(additional_indexes=extra,seconds=seconds,actual_count=len(batch)))
    run.emit('insert_benchmark',runs=timings,actual_count=n)
