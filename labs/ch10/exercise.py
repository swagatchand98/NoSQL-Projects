import time
from concurrent.futures import ThreadPoolExecutor
from pymongo.errors import PyMongoError
from labs.shared.core import reset,timed,plot
from labs.shared.replication import ready,wait_members

class StockRejected(Exception):pass


def transaction(client, operation):
    deadline=time.monotonic()+30
    with client.start_session() as session:
        for attempt in range(10):
            session.start_transaction()
            try:
                value=operation(session)
                while True:
                    try:
                        session.commit_transaction();return value
                    except PyMongoError as exc:
                        if exc.has_error_label('UnknownTransactionCommitResult') and time.monotonic()<deadline:
                            time.sleep(.05);continue
                        raise
            except Exception as exc:
                if session.in_transaction:session.abort_transaction()
                if isinstance(exc,PyMongoError) and exc.has_error_label('TransientTransactionError') and time.monotonic()<deadline:
                    time.sleep(min(.02*2**attempt,.5));continue
                raise
    raise TimeoutError('Transaction retry budget exhausted')


def main(run):
    client=ready();wait_members(client);db=client.college_ch10
    accounts=reset(db,'accounts',[{'_id':'ACC-001','account_id':'ACC-001','holder':'Arjun','balance':500000},{'_id':'ACC-002','account_id':'ACC-002','holder':'Sneha','balance':300000},{'_id':'ACC-003','account_id':'ACC-003','holder':'Rahul','balance':100000}]);history=reset(db,'history')
    def transfer(amount,identifier):
        def body(session):
            if accounts.update_one({'_id':'ACC-001','balance':{'$gte':amount}},{'$inc':{'balance':-amount}},session=session).modified_count!=1:raise StockRejected('Insufficient funds')
            accounts.update_one({'_id':'ACC-002'},{'$inc':{'balance':amount}},session=session)
            history.insert_one({'_id':identifier,'amount_cents':amount},session=session)
        transaction(client,body)
    run.emit('money_units',unit='integer cents',note='Original faculty account balances represented as cents to avoid floating-point money errors')
    transfer(10000,'success');before=list(accounts.find().sort('_id'));history_before=list(history.find())
    try:transfer(99999999,'failure')
    except StockRejected:pass
    after=list(accounts.find().sort('_id'));assert before==after and history_before==list(history.find())
    run.emit('rollback',before=before,after=after,history_before=history_before,history_after=list(history.find()))
    def experiment(workers,requests,stock,use_transaction=True):
        inventory=reset(db,'inventory',[{'_id':'product','stock':stock,'version':0}]);orders=reset(db,'pending_orders')
        def reserve(i):
            def body(session=None):
                doc=inventory.find_one({'_id':'product'},session=session)
                if doc['stock']<1:raise StockRejected()
                result=inventory.update_one({'_id':'product','stock':{'$gt':0},'version':doc['version']},{'$inc':{'stock':-1,'version':1}},session=session)
                if not result.modified_count:raise RuntimeError('Unexpected version conflict')
                orders.insert_one({'_id':i,'quantity':1,'status':'pending'},session=session)
            try:
                if use_transaction:transaction(client,body)
                else:
                    if not inventory.update_one({'_id':'product','stock':{'$gt':0}},{'$inc':{'stock':-1,'version':1}}).modified_count:raise StockRejected()
                return 'reserved'
            except StockRejected:return 'stock_rejected'
        def execute():
            with ThreadPoolExecutor(max_workers=workers) as pool:return list(pool.map(reserve,range(requests)))
        values,seconds=timed(execute)
        return dict(threads=workers,actual_count=requests,successes=values.count('reserved'),stock_rejections=values.count('stock_rejected'),orders=orders.count_documents({}),remaining=inventory.find_one() ['stock'],seconds=seconds,throughput=requests/seconds)
    race=experiment(8,8,5);assert (race['successes'],race['stock_rejections'],race['orders'],race['remaining'])==(5,3,5,0);run.emit('reservation',**race)
    samples=[]
    for threads in [1,4,8,16]:
        n=run.count(1000,40)
        result=experiment(threads,n,n);samples.append(result);run.emit('transaction_benchmark',**result)
        run.emit('atomic_benchmark',**experiment(threads,n,n,False))
    plot(run,'throughput.png',[x['threads'] for x in samples],[x['throughput'] for x in samples],'Threads','Requests/second')
    run.emit('tradeoff',text='Single-document decrement is atomic but does not create a separately consistent order.')
