import datetime
import os

import pymongo
from pymongo.collection import ReturnDocument


db = pymongo.MongoClient("mongo",
                         port=27017,
                         username=os.environ['MONGO_INITDB_ROOT_USERNAME'],
                         password=os.environ['MONGO_INITDB_ROOT_PASSWORD'])

collection = db["face_detection"]["results"]


def post_document(result: dict, image_name: str):
    document = {"image_name": image_name,
                "request_id": result["request_id"],
                "faces": result["faces"],
                "image_id": result["image_id"],
                "time_used": result["time_used"],
                "date": datetime.datetime.utcnow()}
    post_id = collection.insert_one(document).inserted_id
    return post_id


def remove_document(image_id: str):
    collection.delete_one({'image_id': image_id})

def get_document(image_id: str):
    document = collection.find_one({'image_id': image_id})
    return document

def update_document(image_id, result):
    document = {"request_id": result["request_id"],
                "faces": result["faces"],
                "time_used": result["time_used"],
                "date": datetime.datetime.utcnow()}
    document = collection.find_one_and_update({"image_id": image_id}, {'$set': document},
                                              return_document=ReturnDocument.AFTER)
    return document
