from labs.shared.core import reset,timed,seed_data
from labs.shared.polyglot import Backends
from labs.ch16.service import FraudQueryService

def main(run):
    back=Backends()
    try:
        enrollments=[]
        for c in seed_data('courses'):
            for s in c['enrolled_students']:enrollments.append(dict(student=s['email'],course=c['course_code'],instructor=c['instructor']))
        col=reset(back.mongo.college_ch16,'enrollments',enrollments)
        cs=back.cassandra
        for table,key,other in [('by_student','student','course'),('by_course','course','student'),('by_instructor','instructor','student,course')]:
            cs.execute(f'DROP TABLE IF EXISTS {table}')
            cs.execute(f'CREATE TABLE {table} (student text,course text,instructor text,PRIMARY KEY ({key},{other}))')
            prepared=cs.prepare(f'INSERT INTO {table} (student,course,instructor) VALUES (?,?,?)')
            for e in enrollments:cs.execute(prepared,(e['student'],e['course'],e['instructor']))
        back.cypher('MATCH (n) WHERE n:LabStudent OR n:LabCourse DETACH DELETE n')
        for e in enrollments:back.cypher('MERGE(s:LabStudent {id:$student}) MERGE(c:LabCourse {id:$course}) SET c.instructor=$instructor MERGE(s)-[:ENROLLED]->(c)',student=e['student'],course=e['course'],instructor=e['instructor'])
        for field,value,table in [('student','arjun@college.edu','by_student'),('course','AIML101','by_course'),('instructor','Dr. Priya Sharma','by_instructor')]:
            mongo={(e['student'],e['course'],e['instructor']) for e in col.find({field:value})}
            cassandra={(e.student,e.course,e.instructor) for e in cs.execute(f'SELECT * FROM {table} WHERE {field}=%s',(value,))}
            predicate={'student':'s.id','course':'c.id','instructor':'c.instructor'}[field]
            graph={(e['student'],e['course'],e['instructor']) for e in back.cypher(f'MATCH(s:LabStudent)-[:ENROLLED]->(c:LabCourse) WHERE {predicate}=$value RETURN s.id AS student,c.id AS course,c.instructor AS instructor',value=value)}
            assert mongo==cassandra==graph
            run.emit('enrollment_query',query=field,actual_count=len(mongo),results=sorted(mongo),faculty_mapping='Provisional: assigned enrollment queries missing in reference')
        reset(back.mongo.college_ch16,'transactions',[{'_id':'TX-1','user_id':'U1','amount':100}])
        cs.execute('CREATE TABLE IF NOT EXISTS profiles (user_id text PRIMARY KEY, name text)')
        cs.execute('INSERT INTO profiles (user_id,name) VALUES (%s,%s)',('U1','Arjun'))
        back.cypher('MATCH(n:LabUser) DETACH DELETE n')
        back.cypher('CREATE(a:LabUser {id:"U1"})-[:SHARES_DEVICE]->(b:LabUser {id:"U2"})-[:SHARES_DEVICE]->(c:LabUser {id:"U3"})-[:SHARES_DEVICE]->(a)')
        service=FraudQueryService(back.mongo.college_ch16,cs,back.cypher)
        result,seconds=timed(lambda:service.investigate('TX-1'))
        assert result['transaction']['_id']=='TX-1' and len(result['ring_candidates'])==2
        run.emit('real_integration',seconds=seconds,result=result)
    finally:back.close()
