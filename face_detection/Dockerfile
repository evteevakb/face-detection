FROM python:3.10.4-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip3 install --upgrade pip

COPY ./requirements.txt requirements.txt
RUN pip3 install -U -r requirements.txt

COPY . .
