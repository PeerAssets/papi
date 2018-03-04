FROM python:3-alpine3.7

ENV USERNAME=peerassets \
    APP_DIRECTORY=/usr/src/app

RUN addgroup -S ${USERNAME} \
    && adduser -D -H -S -s /bin/false -u 1000 -G ${USERNAME} ${USERNAME} \
    && apk add --update \
        git \
    && rm -rf /var/cache/apk/* \
    && mkdir -p /home/${USERNAME}/.ppcoin \
    && touch /home/${USERNAME}/.ppcoin/ppcoin.conf

COPY requirements.txt ${APP_DIRECTORY}/

WORKDIR ${APP_DIRECTORY}

RUN pip3 install --no-cache-dir -r requirements.txt

COPY papi/ ${APP_DIRECTORY}/

RUN chown -R ${USERNAME}:${USERNAME} ${APP_DIRECTORY} \
    && chown -R ${USERNAME}:${USERNAME} /home/${USERNAME}/.ppcoin

USER ${USERNAME}

EXPOSE 5555

ENTRYPOINT [ "python3", "app.py"]
