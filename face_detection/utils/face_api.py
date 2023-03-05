import base64
import os
from pathlib import Path

import requests


FACE_API = os.environ['FACE_API']
FACE_KEY = os.environ['FACE_KEY']
FACE_SECRET = os.environ['FACE_SECRET']


def detect_faces(local_path: Path, timeout: int = 600):
    with open(local_path, "rb") as image:
        image64 = base64.b64encode(image.read())
    try:
        result = requests.post(FACE_API, data={
            "api_key": FACE_KEY,
            "api_secret": FACE_SECRET,
            "image_base64": image64,
            }, timeout=timeout)
        if result.status_code == 200:
            return result.json()
    except Exception as e:
        print('Error:')
        print(e)
    finally:
        del image64
