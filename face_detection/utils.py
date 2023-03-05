import base64
import datetime
from io import BytesIO
import os
from pathlib import Path
from typing import Union

from minio import Minio, S3Error
from PIL import Image
from pymongo import MongoClient
from pymongo.collection import ReturnDocument
import requests


class FaceAPI:
    def __init__(self):
        self.face_api = os.environ["FACE_API"]
        self.face_key = os.environ["FACE_KEY"]
        self.face_secret = os.environ["FACE_SECRET"]

    def detect(self, local_path: Path, timeout: int = 600):
        with open(local_path, "rb") as image:
            image64 = base64.b64encode(image.read())
        result = requests.post(self.face_api, data={"api_key": self.face_key,
                                                    "api_secret": self.face_secret,
                                                    "image_base64": image64},
                               timeout=timeout)
        if result.status_code != 200:
            result["status_code"] = result.status_code
        return result.json()


class MinioClient:
    def __init__(self):
        self.bucket = os.environ["INITIAL_BUCKET_NAME"]
        self.minio = Minio("localhost:9000", access_key=os.environ["MINIO_ROOT_USER"],
                           secret_key=os.environ["MINIO_ROOT_PASSWORD"], secure=True)

    def load_object(self, local_path: Union[str, Path], image_id: int):
        if isinstance(local_path, str):
            local_path = Path(local_path)
        image_name = f"{image_id}{local_path.suffix}"
        result = self.minio.fput_object(self.bucket, image_name, local_path)
        return result.object_name

    def get_object(self, object_name: str):
        try:
            response = self.minio.get_object(self.bucket, object_name)
            image = Image.open(BytesIO(response.read()))
            return image
        finally:
            response.close()
            response.release_conn()

    def remove_object(self, object_name: str):
        self.minio.remove_object(self.bucket, object_name)


    def replace_object(self, local_path, object_name, image_id):
        self.remove_object(object_name)
        object_name = self.load_object(local_path, image_id)
        return object_name


class Mongo:
    def __init__(self):
        self.database = MongoClient("mongo", port=27017,
                                    username=os.environ["MONGO_INITDB_ROOT_USERNAME"],
                                    password=os.environ["MONGO_INITDB_ROOT_PASSWORD"])
        self.collection = self.database[os.environ["DATABASE_NAME"]][os.environ["COLLECTION_NAME"]]

    def post_document(self, result: dict, image_name: str):
        document = {"image_name": image_name,
                    "request_id": result["request_id"],
                    "faces": result["faces"],
                    "image_id": result["image_id"],
                    "time_used": result["time_used"],
                    "date": datetime.datetime.utcnow()}
        post_id = self.collection.insert_one(document).inserted_id
        return post_id

    def remove_document(self, image_id: str):
        self.collection.delete_one({'image_id': image_id})

    def get_document(self, image_id: str):
        document = self.collection.find_one({'image_id': image_id})
        return document

    def update_document(self, image_id, result):
        document = {"request_id": result["request_id"],
                    "faces": result["faces"],
                    "time_used": result["time_used"],
                    "date": datetime.datetime.utcnow()}
        document = self.collection.find_one_and_update({"image_id": image_id}, {'$set': document},
                                                       return_document=ReturnDocument.AFTER)
        return document
