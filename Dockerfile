FROM python:3.12-slim

LABEL maintainer="irakirvas78@gmail.com"

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt requirements.txt

RUN apt-get update && apt-get install -y \
    libpq-dev gcc \
 && pip install --no-cache-dir -r requirements.txt \
 && apt-get purge -y gcc \
 && rm -rf /var/lib/apt/lists/*

COPY . .

RUN mkdir -p /app/media

RUN adduser \
    --disabled-password \
    --no-create-home \
    django-user

RUN chown -R django-user /app/media
RUN chmod -R 755 /app/media

USER django-user
