FROM alpine:latest
MAINTAINER luizbragaa@gmail.com

ENV RUNTIME_PACKAGES python py-pip libxslt libxml2 bash ca-certificates openssl
ENV BUILD_PACKAGES build-base libxslt-dev libxml2-dev libffi-dev python-dev openssl-dev git

WORKDIR /scrapyd

ADD requirements.txt .
RUN apk add --update $RUNTIME_PACKAGES && rm -rf /var/cache/apk/*
RUN apk --update add $BUILD_PACKAGES && \
  pip --no-cache-dir install -r requirements.txt && \
  update-ca-certificates && \
  apk del $BUILD_PACKAGES && \
  rm -rf /var/cache/apk/*

ADD ./docker_build/scrapyd/scrapyd.cfg /etc/scrapyd/scrapyd.conf

WORKDIR /scrapyd/app
ADD . .
RUN python setup.py install

CMD ["scrapyd"]
