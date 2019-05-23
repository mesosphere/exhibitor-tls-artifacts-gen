FROM alpine:3.9

RUN apk update && \
    apk add gcc openjdk8 python3 python3-dev make musl-dev libffi-dev openssl openssl-dev

WORKDIR /src
COPY requirements.txt /src

RUN pip3 install -r requirements.txt

ADD . /src
RUN pip3 install -e .

ENTRYPOINT ["/usr/bin/exhibitor-tls-artifacts"]
