"""Tenant identity is exclusively derived from a verified JWT."""
import os,time
from datetime import datetime,timezone,timedelta
from typing import Literal
import jwt
from fastapi import FastAPI,Depends,HTTPException,Header
from pydantic import BaseModel,Field
from pymongo import MongoClient,ReturnDocument
from pymongo.errors import DuplicateKeyError
import uuid

app=FastAPI(title='Chapter 15 task API')
client=MongoClient(os.getenv('MONGO_URI','mongodb://localhost:27017'),serverSelectionTimeoutMS=5000)
db=client.college_ch15

class TaskInput(BaseModel):
    title:str=Field(min_length=1,max_length=200)
    status:Literal['pending','done']='pending'


def identity(authorization:str=Header(default='')):
    secret=os.getenv('JWT_SECRET')
    if not secret:raise HTTPException(503,'JWT_SECRET is not configured')
    try:
        if not authorization.startswith('Bearer '):raise ValueError()
        claims=jwt.decode(authorization[7:],secret,algorithms=['HS256'],audience='college-labs',issuer='college-lab-issuer',options={'require':['exp','sub','tenant_id','role','iss','aud']})
        if claims['role'] not in ['member','tenant-admin'] or not isinstance(claims['tenant_id'],str):raise ValueError()
    except (jwt.PyJWTError,ValueError,KeyError):raise HTTPException(401,'Invalid token')
    window=int(time.time())//60
    key=f"{claims['tenant_id']}:{window}"
    db.rate_limits.create_index('expires_at',expireAfterSeconds=0)
    try:
        doc=db.rate_limits.find_one_and_update({'_id':key},{'$inc':{'count':1},'$setOnInsert':{'expires_at':datetime.now(timezone.utc)+timedelta(minutes=2)}},upsert=True,return_document=ReturnDocument.AFTER)
    except DuplicateKeyError:
        doc=db.rate_limits.find_one_and_update({'_id':key},{'$inc':{'count':1}},return_document=ReturnDocument.AFTER)
    if doc['count']>int(os.getenv('RATE_LIMIT','100')):raise HTTPException(429,'Tenant request limit exceeded')
    return claims


def scoped(user,task_id=None):
    query={'tenant_id':user['tenant_id']}
    if task_id:query['_id']=task_id
    if user['role']!='tenant-admin':query['owner_id']=user['sub']
    return query


@app.get('/tasks')
def listing(user=Depends(identity)):
    db.tasks.create_index([('tenant_id',1),('created_at',1)])
    return list(db.tasks.find(scoped(user)).sort('created_at',1).limit(100))


@app.post('/tasks',status_code=201)
def create(data:TaskInput,user=Depends(identity)):
    doc=dict(_id=str(uuid.uuid4()),tenant_id=user['tenant_id'],owner_id=user['sub'],created_at=datetime.now(timezone.utc),**data.model_dump())
    db.tasks.insert_one(doc);return doc


@app.get('/tasks/{task_id}')
def read(task_id:str,user=Depends(identity)):
    doc=db.tasks.find_one(scoped(user,task_id))
    if doc is None:raise HTTPException(404,'Task not found')
    return doc


@app.patch('/tasks/{task_id}')
def update(task_id:str,data:TaskInput,user=Depends(identity)):
    doc=db.tasks.find_one_and_update(scoped(user,task_id),{'$set':data.model_dump()},return_document=ReturnDocument.AFTER)
    if doc is None:raise HTTPException(404,'Task not found')
    return doc


@app.delete('/tasks/{task_id}',status_code=204)
def delete(task_id:str,user=Depends(identity)):
    if not db.tasks.delete_one(scoped(user,task_id)).deleted_count:raise HTTPException(404,'Task not found')
