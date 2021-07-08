FROM alpine:latest
LABEL maintainer="IBM Frederic Spiers <frederic.spiers-isc.france@ibm.com>" \
      component="deployment-tool"

ARG TZ="Europe/Paris"

ENV TZ=$TZ

RUN echo "http://dl-cdn.alpinelinux.org/alpine/edge/main" >> /etc/apk/repositories \
    && echo "http://dl-cdn.alpinelinux.org/alpine/edge/community" >> /etc/apk/repositories \
    && apk update --no-cache \
    && apk upgrade --no-cache \  
    && apk add --no-cache --update \
    bash \
    skopeo \
    python3 \
    jq \
    py3-pip

COPY ./skopeoTransfer.py ./skopeolib.py ./getImage-proxy.sh ./getImage-hostnet.sh /app/

WORKDIR /app

ENTRYPOINT ["python3","skopeoTransfer.py"]