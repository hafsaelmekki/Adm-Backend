from sqlite3 import Date
import uuid
from typing import Optional
from pydantic import BaseModel, Field
from datetime import date, datetime, time, timedelta
from bson.objectid import ObjectId



class Adm_comments_dataset(BaseModel):
    id: str 
    Text : str
    Sentiment : str
    Dialect : str
    posting_date : datetime

    class Config:
        schema_extra = {
            "example": {
                "Text": "Don Quixote",
                "Sentiment": "Miguel de Cervantes",
                "Dialect": "...",
                "posting_date" : " "

            }
        }
        