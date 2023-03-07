import base64
import datetime
from io import BytesIO
import os
from typing import Dict

from minio import Minio
from PIL import Image
from pymongo import MongoClient
from pymongo.collection import ReturnDocument
import requests


class FaceAPI:
    def __init__(self) -> None:
        self.face_api = os.environ["FACE_API"]
        self.face_key = os.environ["FACE_KEY"]
        self.face_secret = os.environ["FACE_SECRET"]

    def detect(self, image: bytes, timeout: int = 600) -> Dict:
        image64 = base64.b64encode(image)
        response = requests.post(self.face_api, data={"api_key": self.face_key,
                                                      "api_secret": self.face_secret,
                                                      "image_base64": image64},
                                 timeout=timeout)
        result = response.json()
        if response.status_code != 200:
            result["status_code"] = response.status_code
        return result


class MinioClient:
    def __init__(self) -> None:
        self.bucket = os.environ["INITIAL_BUCKET_NAME"]
        self.minio = Minio("minio:9000", access_key=os.environ["MINIO_ROOT_USER"],
                           secret_key=os.environ["MINIO_ROOT_PASSWORD"], secure=False)

    def load_object(self, content: bytes, image_id: str) -> None:
        content = BytesIO(content)
        self.minio.put_object(bucket_name=self.bucket, object_name=image_id,
                              data=content, length=content.getbuffer().nbytes)

    def get_object(self, object_name: str) -> Image:
        response = self.minio.get_object(self.bucket, object_name)
        image = Image.open(BytesIO(response.read()))
        return image

    def remove_object(self, image_id: str) -> None:
        self.minio.remove_object(self.bucket, image_id)

    def replace_object(self, content: bytes, image_id: str) -> None:
        self.remove_object(image_id)
        self.load_object(content, image_id)


class Mongo:
    def __init__(self) -> None:
        self.database = MongoClient("mongo", port=27017,
                                    username=os.environ["MONGO_INITDB_ROOT_USERNAME"],
                                    password=os.environ["MONGO_INITDB_ROOT_PASSWORD"])
        self.collection = self.database[os.environ["DATABASE_NAME"]][os.environ["COLLECTION_NAME"]]

    def post_document(self, result: Dict) -> None:
        document = {"request_id": result["request_id"],
                    "faces": result["faces"],
                    "image_id": result["image_id"],
                    "time_used": result["time_used"],
                    "date": datetime.datetime.utcnow()}
        if self.collection.count_documents({"image_id": result["image_id"]}, limit=1) == 0:
            self.collection.insert_one(document)

    def remove_document(self, image_id: str) -> None:
        self.collection.delete_one({"image_id": image_id})

    def get_document(self, image_id: str) -> Dict:
        return self.collection.find_one({"image_id": image_id})

    def update_document(self, image_id: str, result: Dict) -> None:
        document = {"request_id": result["request_id"],
                    "faces": result["faces"],
                    "time_used": result["time_used"],
                    "date": datetime.datetime.utcnow()}
        self.collection.find_one_and_update({"image_id": image_id},
                                            {"$set": document},
                                            return_document=ReturnDocument.AFTER)
