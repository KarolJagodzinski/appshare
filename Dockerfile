# pull official base image
FROM python:3.7.5-alpine3.10

# set work directory
WORKDIR /app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DEBUG 0
ENV DJANGO_SETTINGS_MODULE "appshare.settings.main"

RUN apk update \
    && apk add --virtual build-deps gcc python3-dev musl-dev \
    && apk add postgresql-dev \
    && pip install psycopg2 \
    && apk del build-deps


COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN python manage.py migrate
RUN python manage.py collectstatic --noinput

# run gunicorn
CMD gunicorn appshare.wsgi:application --bind 0.0.0.0:$PORT
