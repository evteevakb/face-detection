from pathlib import Path
from typing import Union

from fastapi import FastAPI
from PIL import ImageDraw

app = FastAPI()

from utils.face_api import detect_faces
from utils.mongodb import post_document, get_document, remove_document, update_document
from utils.minio_api import get_object, load_object, remove_object, replace_object



@app.post("/image")
def detect(local_path: Union[str, Path]) -> dict:
    if isinstance(local_path, str):
        local_path = Path(local_path)
    result = detect_faces(local_path)
    image_id = result["image_id"]
    image_name = load_object(local_path, image_id)
    post_document(result, image_name)
    return {"id": image_id}


@app.get("/image/<id>?color=<red/green/blue>")
def get(image_id, color):
    document = get_document(image_id)
    image = get_object(document["image_name"])
    draw = ImageDraw.Draw(image)
    for face in document["faces"]:
        bbox = face["face_rectangle"]
        print(bbox)
        draw.rectangle([bbox["left"], bbox["top"],
                        bbox["left"]+bbox["width"], bbox["top"]+bbox["height"]],
                       fill=None, outline=color, width=1)
    return image


@app.put("/image/<id>")
def put(local_path, image_id):
    if isinstance(local_path, str):
        local_path = Path(local_path)
    result = detect_faces(local_path)
    document = update_document(image_id, result)
    replace_object(local_path, document["image_name"], document["image_id"])

@app.delete("/image/<id>")
def remove(image_id):
    document = get_document(image_id)
    object_name = document["image_name"]
    remove_object(object_name)
    remove_document(object_name)
