FROM python:3-alpine3.7

ENV USERNAME=papi \
    APP_DIRECTORY=/usr/src/app

RUN addgroup -S ${USERNAME} \
    && adduser -D -H -S -s /bin/false -u 1000 -G ${USERNAME} ${USERNAME} \
    && apk add --update \
        git \
    && rm -rf /var/cache/apk/*

COPY requirements.txt ${APP_DIRECTORY}/

WORKDIR ${APP_DIRECTORY}

RUN pip3 install --no-cache-dir -r requirements.txt

COPY papi/ ${APP_DIRECTORY}/

RUN chown -R ${USERNAME}:${USERNAME} ${APP_DIRECTORY}

USER ${USERNAME}

ENV APP_ENV=docker

VOLUME /var/lib/papi/

EXPOSE 5555

ENTRYPOINT [ "python3", "app.py"]
