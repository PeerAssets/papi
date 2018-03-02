FROM debian:stable-slim

LABEL maintainer.0="Peerchemist (@peerchemist)"

RUN apt-get update -y && \
    apt-get install -y python3-pip python3-dev git

# We copy just the requirements.txt first to leverage Docker cache
COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip3 install -r requirements.txt

COPY papi/* /app

ENTRYPOINT [ "python3" ]

CMD [ "app.py" ]

## expose port
EXPOSE 5555