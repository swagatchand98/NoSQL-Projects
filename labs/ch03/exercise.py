from labs.shared.core import database, reset, seed_data

def main(run):
    db=database(run)
    courses=seed_data('courses')
    for c in courses:
        c['_id']=c['course_code'];c['prerequisites']=[] if c['course_code']=='AIML101' else ['AIML101']
    col=reset(db,'courses',courses,seed_data('course_validator'))
    run.emit('courses',actual_count=col.count_documents({}),monday=list(col.find({'schedule.days':'Monday'})),instructor_students=list(col.find({'instructor':'Dr. Priya Sharma'},{'enrolled_students':1})))
    from pymongo.errors import WriteError
    try:
        col.insert_one({'course_name':'invalid'})
    except WriteError:
        run.emit('validation_rejected', observed=True)
    else:
        raise AssertionError('validator accepted invalid course')
    if run.activity=='1':return
    posts=reset(db,'posts',[{'_id':i,'title':f'Post {i}'} for i in range(5)])
    comments=reset(db,'comments',[{'_id':i,'post_id':i%5,'text':f'Comment {i}'} for i in range(10)])
    joined=list(posts.aggregate([{'$lookup':{'from':'comments','localField':'_id','foreignField':'post_id','as':'comments'}}]))
    embedded=reset(db,'embedded_posts',joined)
    # Count application database calls explicitly; do not confuse a server-side lookup with N+1.
    ref=posts.find_one({'_id':0}); children=list(comments.find({'post_id':0}))
    emb=embedded.find_one({'_id':0})
    assert sorted(x['_id'] for x in children)==sorted(x['_id'] for x in emb['comments'])
    run.emit('migration',actual_count=embedded.count_documents({}),joined=joined,client_round_trips={'reference_two_queries':2,'lookup':1,'embedded':1})
    run.emit('design',prerequisites='Reference course IDs: shared courses change independently.',large_comments='Keep 10,000 comments referenced and paginate; unbounded arrays grow toward the 16 MiB BSON limit.')
