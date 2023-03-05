from io import BytesIO
import os
from pathlib import Path
from typing import Union

from minio import Minio
from PIL import Image


BUCKET = os.environ['INITIAL_BUCKET_NAME']
MINIO_CLIENT = Minio("localhost:9000", access_key=os.environ['MINIO_ROOT_USER'],
                     secret_key=os.environ['MINIO_ROOT_PASSWORD'], secure=True)


def load_object(local_path: Union[str, Path], image_id: int):
    if isinstance(local_path, str):
        local_path = Path(local_path)
    image_name = f"{image_id}{local_path.suffix}"
    result = MINIO_CLIENT.fput_object(BUCKET, image_name, local_path)
    return result.object_name


def get_object(object_name: str):
    try:
        response = MINIO_CLIENT.get_object(BUCKET, object_name)
        image = Image.open(BytesIO(response.read()))
        return image
    finally:
        response.close()
        response.release_conn()


def remove_object(object_name: str):
    MINIO_CLIENT.remove_object(BUCKET, object_name)


def replace_object(local_path, object_name, image_id):
    remove_object(object_name)
    object_name = load_object(local_path, image_id)
    return object_name
