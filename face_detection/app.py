from pathlib import Path
from typing import Union

from fastapi import FastAPI, HTTPException
from PIL import ImageDraw

from utils import FaceAPI, MinioClient, Mongo


app = FastAPI()
face_api = FaceAPI()
minio = MinioClient()
mongo = Mongo()


@app.post("/image")
def detect(local_path: Union[str, Path]) -> dict:
    if isinstance(local_path, str):
        local_path = Path(local_path)
    result = face_api.detect(local_path)
    if "error_message" in result:
        raise HTTPException(status_code=result["status_code"], detail=result["error_message"])
    if len(result["faces"]) == 0:
        raise HTTPException(status_code=404, detail=f"Faces on the image {local_path} not found")
    image_id = result["image_id"]
    image_name = minio.load_object(local_path, image_id)
    mongo.post_document(result, image_name)
    return {"id": image_id}


@app.get("/image/<id>?color=<red/green/blue>")
def get(image_id, color):
    document = mongo.get_document(image_id)
    image = minio.get_object(document["image_name"])
    draw = ImageDraw.Draw(image)
    for face in document["faces"]:
        bbox = face["face_rectangle"]
        draw.rectangle([bbox["left"], bbox["top"],
                        bbox["left"]+bbox["width"], bbox["top"]+bbox["height"]],
                       fill=None, outline=color, width=1)
    return image


@app.put("/image/<id>")
def put(local_path, image_id):
    if isinstance(local_path, str):
        local_path = Path(local_path)
    result = face_api.detect(local_path)
    document = mongo.update_document(image_id, result)
    minio.replace_object(local_path, document["image_name"], document["image_id"])


@app.delete("/image/<id>")
def remove(image_id):
    document = mongo.get_document(image_id)
    object_name = document["image_name"]
    minio.remove_object(object_name)
    mongo.remove_document(object_name)
