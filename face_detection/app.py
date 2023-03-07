import io
from enum import Enum
import logging
from typing import Dict

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import Response
from PIL import ImageDraw

from utils import FaceAPI, MinioClient, Mongo


class Colors(str, Enum):
    RED = "red"
    GREEN = "green"
    BLUE = "blue"


app = FastAPI()
face_api = FaceAPI()
minio = MinioClient()
mongo = Mongo()


# setup logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
screen_logs = logging.StreamHandler()
file_logs = logging.handlers.RotatingFileHandler("app.log", mode="a",
                                                 maxBytes = 100*1024, backupCount = 3)
formatter = logging.Formatter(
    "%(asctime)s - %(module)s - %(funcName)s - line:%(lineno)d - %(levelname)s - %(message)s")
screen_logs.setFormatter(formatter)
file_logs.setFormatter(formatter)
logger.addHandler(screen_logs)
logger.addHandler(file_logs)


@app.get("/")
async def root() -> Dict:
    return {"message": "Welcome to face detection application based on Face++ and FastAPI"}


@app.post("/image")
async def detect(file: UploadFile = File(...)) -> Dict:
    image = await file.read()
    result = face_api.detect(image)
    if "error_message" in result:
        raise HTTPException(status_code=result["status_code"], detail=result["error_message"])
    if len(result["faces"]) == 0:
        raise HTTPException(status_code=404, detail="Faces on the image are not found")
    image_id = result["image_id"]
    try:
        minio.load_object(image, image_id)
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Could not connect to MinIO storage") from exc
    mongo.post_document(result)
    return {"id": image_id}


@app.get("/image/{image_id}", response_class=Response)
async def get(image_id: str, color: Colors) -> Response:
    document = mongo.get_document(image_id)
    if document is None:
        raise HTTPException(status_code=404, detail=f"Image with image_id={image_id} not found")
    image = minio.get_object(image_id)
    draw = ImageDraw.Draw(image)
    for face in document["faces"]:
        bbox = face["face_rectangle"]
        draw.rectangle([bbox["left"], bbox["top"],
                        bbox["left"]+bbox["width"], bbox["top"]+bbox["height"]],
                       fill=None, outline=color, width=1)
    image_bytes = io.BytesIO()
    image.save(image_bytes, format="PNG")
    image_bytes = image_bytes.getvalue()
    return Response(content=image_bytes, media_type="image/png")


@app.put("/image/{image_id}")
async def put(image_id: str, file: UploadFile = File(...)) -> Dict:
    image = await file.read()
    result = face_api.detect(image)
    if "error_message" in result:
        raise HTTPException(status_code=result["status_code"], detail=result["error_message"])
    if len(result["faces"]) == 0:
        raise HTTPException(status_code=404, detail="Faces on the image are not found")
    mongo.update_document(image_id, result)
    minio.replace_object(image, image_id)
    return {"id": image_id}


@app.delete("/image/{image_id}")
def remove(image_id: str) -> Dict:
    minio.remove_object(image_id)
    mongo.remove_document(image_id)
    return {"id": image_id}
