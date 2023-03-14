FROM python:3.10.4-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY . /face_detection
WORKDIR /face_detection

RUN pip3 install --upgrade pip
RUN pip3 install -U -r requirements.txt