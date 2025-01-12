# pull official base image
FROM python:3.11.4-slim-buster

WORKDIR /aetheranime_backend

COPY aetheranime /aetheranime_backend

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DJANGO_DEBUG=False


RUN pip install --upgrade pip

RUN pip install -r requirements.txt

CMD ["gunicorn", "aetheranime.wsgi:application", "--bind", "0.0.0.0:8000"]
