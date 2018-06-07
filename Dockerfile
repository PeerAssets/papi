FROM tiangolo/uwsgi-nginx-flask:python3.6-alpine3.7

RUN apk --update --no-cache add build-base \
    && apk add postgresql-dev git \
    && python3 -m pip install psycopg2 --no-cache-dir \
    && apk --purge del build-base \
    && rm -rf /var/cache/apk/*

COPY requirements.txt /app

RUN pip install --no-cache-dir -r requirements.txt

COPY ./app /app

ENV APP_ENV=docker

ENV LISTEN_PORT 5555

EXPOSE 5555