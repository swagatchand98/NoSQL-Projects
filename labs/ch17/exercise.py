import json,os,time
from pathlib import Path
from labs.shared.core import database,reset,Blocked,timed,plot

def main(run):
    if run.activity in ('all','1'):rag(run)
    if run.activity in ('all','2'):benchmark(run)


def rag(run):
    uri=os.getenv('MONGO_URI_ATLAS')
    if not uri:
        run.emit('external_check_blocked',check='Atlas RAG',reason='MONGO_URI_ATLAS not configured');return
    from sentence_transformers import SentenceTransformer
    from pymongo import MongoClient
    from pymongo.operations import SearchIndexModel
    model=SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    records=json.loads(Path('data/defensive-documents.json').read_text())
    chunks=[]
    for record in records:
        words=record['text'].split()
        for start in range(0,len(words),100):
            text=' '.join(words[start:start+100]);chunks.append(dict(_id=f"{record['_id']}-{start}",source=record['source'],text=text,record_id=record['_id']))
    vectors=model.encode([x['text'] for x in chunks],normalize_embeddings=True)
    for chunk,vector in zip(chunks,vectors):chunk['vector']=vector.tolist()
    with MongoClient(uri,serverSelectionTimeoutMS=10000) as client:
        col=client.college_ch17.chunks
        for chunk in chunks:col.replace_one({'_id':chunk['_id']},chunk,upsert=True)
        name='threat_vectors'
        definition={'fields':[{'type':'vector','path':'vector','numDimensions':384,'similarity':'cosine'}]}
        indexes=list(col.list_search_indexes())
        if not any(x['name']==name for x in indexes):col.create_search_index(SearchIndexModel(definition=definition,name=name,type='vectorSearch'))
        deadline=time.monotonic()+300
        while not any(x.get('queryable') for x in col.list_search_indexes(name)):
            if time.monotonic()>deadline:raise Blocked('Atlas index not queryable within five minutes')
            time.sleep(5)
        question='Which OpenSSH vulnerability needs patching?'
        vector=model.encode(question,normalize_embeddings=True).tolist()
        result=list(col.aggregate([{'$vectorSearch':{'index':name,'path':'vector','queryVector':vector,'numCandidates':100,'limit':3}},{'$project':{'vector':0}}]))
        run.emit('atlas_retrieval',actual_count=len(chunks),top_three=result,index=definition,embedding_model='sentence-transformers/all-MiniLM-L6-v2')
        from app.rag import generate_and_store
        response=generate_and_store(client.college_ch17,'chapter17-demo',question,result)
        run.emit('atlas_sourced_answer',response=response)
        response=generate_and_store(client.college_ch17,'chapter17-demo','What should I do about the first one?',result[:1])
        run.emit('atlas_follow_up',response=response)


def benchmark(run):
    import numpy as np,faiss
    rng=np.random.default_rng(42);n=run.count(5000,1000);queries_count=run.count(100,20)
    data=rng.normal(size=(n,384)).astype('float32');queries=rng.normal(size=(queries_count,384)).astype('float32')
    faiss.normalize_L2(data);faiss.normalize_L2(queries)
    exact=faiss.IndexFlatIP(384);exact.add(data);_,truth=exact.search(queries,20)
    rows=[]
    for kind in ['HNSW','IVF']:
        for effort in [16,64,128]:
            if kind=='HNSW':
                index=faiss.IndexHNSWFlat(384,32,faiss.METRIC_INNER_PRODUCT);index.hnsw.efSearch=effort
            else:
                index=faiss.IndexIVFFlat(faiss.IndexFlatIP(384),384,32,faiss.METRIC_INNER_PRODUCT);index.nprobe=min(32,max(1,effort//4))
            start=time.perf_counter()
            if not index.is_trained:index.train(data)
            index.add(data);build=time.perf_counter()-start
            latencies=[];recalls=[]
            for i,q in enumerate(queries):
                (_,ids),seconds=timed(lambda:index.search(q.reshape(1,-1),20));latencies.append(seconds)
                recalls.append(len(set(ids[0])&set(truth[i]))/20)
            row=dict(backend='local FAISS, not Atlas',kind=kind,effort=effort,build_seconds=build,mean_latency_ms=float(np.mean(latencies)*1000),recall_at_20=float(np.mean(recalls)),actual_count=n,queries=queries_count,dimensions=384)
            rows.append(row);run.emit('vector_benchmark',**row)
    run.save('faiss.json',rows)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,ax=plt.subplots()
    for kind in ['HNSW','IVF']:
        subset=[r for r in rows if r['kind']==kind];ax.plot([r['mean_latency_ms'] for r in subset],[r['recall_at_20'] for r in subset],marker='o',label=kind)
    ax.set(xlabel='Mean query latency (ms)',ylabel='Recall@20',title='Local FAISS — not Atlas');ax.legend();fig.savefig(run.directory/'tradeoff.png');plt.close(fig)
    run.emit('substitution',text='Local comparison satisfies HNSW/IVF algorithm measurement only, not an Atlas-native IVF benchmark. Confirm actual deployment capabilities separately.')
