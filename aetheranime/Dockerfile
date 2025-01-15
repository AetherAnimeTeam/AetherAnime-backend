# pull official base image
FROM python:3.11.4-slim-buster

ENV HOME=/aetheranime_backend
ENV APP_HOME=/aetheranime_backend
RUN mkdir $APP_HOME
RUN mkdir $APP_HOME/staticfiles
WORKDIR $APP_HOME

COPY . /aetheranime_backend


ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DJANGO_DEBUG=False


RUN pip install --upgrade pip

RUN pip install -r requirements.txt --no-cache-dir
