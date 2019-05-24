FROM alpine:3.9

RUN apk update && \
    apk add gcc openjdk8 python3 python3-dev make musl-dev libffi-dev openssl openssl-dev

WORKDIR /src

# Copy the `requirements.txt` file separately so we can keep this Docker image
# layer without re-running the expensive `pip install` command when changing
# files in this repo that have no effect on python dependencies.
COPY requirements.txt /src
RUN pip3 install -r requirements.txt

ADD . /src
RUN pip3 install -e .

ENTRYPOINT ["/usr/bin/exhibitor-tls-artifacts"]
