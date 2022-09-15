from xml.etree.ElementTree import Comment
from fastapi import FastAPI
from models import Adm_comments_dataset
from pymongo import MongoClient
# pprint library is used to make the output look more pretty
from pprint import pprint
from fastapi.middleware.cors import CORSMiddleware
import uuid
from typing import Optional
from pydantic import BaseModel, Field
from datetime import date, datetime, time, timedelta
from bson.objectid import ObjectId
from typing import Dict, Any
import pandas as pd
import pickle

def comment_helper(comment) -> dict:
    return {
        "id": str(comment["_id"]),
        "Text": comment["Text"],
        "Sentiment": comment["Sentiment"],
        "Dialect": comment["Dialect"],
        "posting_date": comment["posting_date"],
    }



app = FastAPI()

origins=[
    "http://localhost:8080/",
     "http://localhost:4200"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"]
)

client = MongoClient('localhost:27017')
db=client.Internship_data
serverStatusResult=db.command("serverStatus")

@app.get("/")
def home():
    return {"message":"Hello World"}

@app.get("/get_all_comments")
def get_all_comments():
    collection = db['Adm_comments_dataset']
    
    cursor1 = collection.aggregate([
    { "$group": {
        "_id": { "$toLower": "$Sentiment" },
        "count": { "$sum": 1 }
    } },
    { "$group": {
        "_id": None,
        "counts": {
            "$push": { "k": "$_id", "v": "$count" }
        }
    } },
    { "$replaceRoot": {
        "newRoot": { "$arrayToObject": "$counts" }
    } }    
])
    cursor2 = collection.aggregate([
    { "$group": {
        "_id": { "$toLower": "$Dialect" },
        "count": { "$sum": 1 }
    } },
    { "$group": {
        "_id": None,
        "counts": {
            "$push": { "k": "$_id", "v": "$count" }
        }
    } },
    { "$replaceRoot": {
        "newRoot": { "$arrayToObject": "$counts" }
    } }    
])
    
    
    for k in cursor1:
        cursor1=k
    for k in cursor2:
        cursor2=k
    return {"Sentiment":cursor1,"Dialect":cursor2}

@app.get("/statistics")
def statistics(from_date,to_date):
    from_date = datetime.strptime(from_date,'%Y-%m-%d')
    to_date= datetime.strptime(to_date,'%Y-%m-%d')
    collection = db['Adm_comments_dataset']
    #cursor1 = collection.find({"posting_date": {"$gte": from_date, "$lt": to_date}})
    cursor2 = collection.aggregate([
    {"$match":{"posting_date": {"$gte": from_date, "$lt": to_date}}},
    { "$group": {
        "_id": { "$toLower": "$Dialect" },
        "count": { "$sum": 1 }
    } },
    { "$group": {
        "_id": None,
        "counts": {
            "$push": { "k": "$_id", "v": "$count" }
        }
    } },
    { "$replaceRoot": {
        "newRoot": { "$arrayToObject": "$counts" }
    } }    
])
    cursor3 = collection.aggregate([
    {"$match":{"posting_date": {"$gte": from_date, "$lt": to_date}}},
    { "$group": {
        "_id": { "$toLower": "$Sentiment" },
        "count": { "$sum": 1 }
    } },
    { "$group": {
        "_id": None,
        "counts": {
            "$push": { "k": "$_id", "v": "$count" }
        }
    } },
    { "$replaceRoot": {
        "newRoot": { "$arrayToObject": "$counts" }
    } }    
])

    for k in cursor3:
        cursor3=k
    for k in cursor2:
        cursor2=k
    return {"Sentiment":cursor3,"Dialect":cursor2}
    #for document in cursor:
    #      print(document)



@app.get("/retrieve_comments")        
def retrieve_comments():
    collection = db['Adm_comments_dataset']
    comments = []
    for comment in collection.find():
        comments.append(comment_helper(comment))
    return comments


@app.delete("/delete_comment")        
def delete_comment(_id):
    collection = db['Adm_comments_dataset']
    collection.delete_one({'_id': ObjectId(_id)})
    return True

@app.put("/update_comment")        
async def update_comment(id,new_comment: Adm_comments_dataset):
    collection = db['Adm_comments_dataset']
    print("this is the new id",id)

    print("this is the new comment",dict(new_comment))

    collection.update_one({"_id": ObjectId(id)},{"$set": dict(new_comment) })
    return True

@app.post("/add_comment")        
async def add_comment(new_comment:Adm_comments_dataset):
    collection = db['Adm_comments_dataset']
    print("this is the new comment",new_comment)

    collection.insert_one(dict(new_comment))
    return True

## Convert to string 
def Convert(string):
    li = list(string.split(" "))
    return li

@app.post("/sentiment_detector")        
async def sentiment_detector(texte : str):
    print(texte)

    filename_S = 'models/Sentiment_detector_model.sav'
    filename_D = 'models/Dialect_detector_model.sav'

    filename_tfidf = 'models/tfidfVectorizer.sav'
    test = Convert(texte)

    print(test)
    # load the tfidfVectorizer from disk
    union = pickle.load(open(filename_tfidf, 'rb'))

    test_vect = union.transform(test)

    # load the model Sentiment from disk
    loaded_model = pickle.load(open(filename_S, 'rb'))
    result_s = loaded_model.predict(test_vect)
    prob_s = loaded_model.predict_proba(test_vect)
    print(prob_s)

    # load the model Dialect from disk
    loaded_model = pickle.load(open(filename_D, 'rb'))
    result_d = loaded_model.predict(test_vect)
    prob_d = loaded_model.predict_proba(test_vect)
    print(prob_d)

    


    return {'sentiment':result_s[0],'dialect':result_d[0],'prob_s':list(prob_s[0]) , 'prob_d':list(prob_d[0])}