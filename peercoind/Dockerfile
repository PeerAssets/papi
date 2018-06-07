FROM peerchemist/peercoind

RUN apk --no-cache add python3 py3-pip \
    && pip3 install --no-cache-dir requests

COPY transaction.py /usr/local/bin
