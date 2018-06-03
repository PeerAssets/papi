FROM postgres

ENV POSTGRES_USER docker

ENV POSTGRES_PASSWORD papipass

ENV POSTGRES_DB papi

ENV PGDATA /var/lib/postgresql/data

FROM tiangolo/uwsgi-nginx-flask:python3.6-alpine3.7

ENV USERNAME=papi \
    APP_DIRECTORY=/app

RUN addgroup -S ${USERNAME} \
    && adduser -D -H -S -s /bin/false -u 1000 -G ${USERNAME} ${USERNAME} \
    && apk add --update \
        --virtual build-deps postgresql-dev postgresql-client python3-dev gcc musl-dev\
    && pip install psycopg2\
    && rm -rf /var/cache/apk/*

WORKDIR ${APP_DIRECTORY}

COPY requirements.txt ${APP_DIRECTORY}/

COPY docker-entrypoint.sh ${APP_DIRECTORY}/

RUN pip install --no-cache-dir -r requirements.txt

COPY papi/ ${APP_DIRECTORY}/

RUN chown -R ${USERNAME}:${USERNAME} ${APP_DIRECTORY}

USER ${USERNAME}

ENV APP_ENV=docker

ENV LISTEN_PORT 5555

EXPOSE 5555

EXPOSE 5432

ENTRYPOINT ["sh","./docker-entrypoint.sh", "--", "python3", "main.py"]
