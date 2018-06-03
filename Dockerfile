FROM tiangolo/uwsgi-nginx-flask:python3.6-alpine3.7

ENV USERNAME=papi \
    APP_DIRECTORY=/app

RUN addgroup -S ${USERNAME} \
    && adduser -D -H -S -s /bin/false -u 1000 -G ${USERNAME} ${USERNAME} \
    && apk --update --no-cache add build-base \
    && apk add postgresql-dev \
    && python3 -m pip install psycopg2 --no-cache-dir \
    && apk --purge del build-base \
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

ENTRYPOINT ["python3", "main.py"]
