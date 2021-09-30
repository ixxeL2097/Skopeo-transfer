FROM alpine:latest

LABEL maintainer="IBM Frederic Spiers <fredspiers@gmail.com>" \
      component="deployment-tool"

ENV TZ="Europe/Paris"

RUN echo "http://dl-cdn.alpinelinux.org/alpine/edge/main" >> /etc/apk/repositories \
    && echo "http://dl-cdn.alpinelinux.org/alpine/edge/community" >> /etc/apk/repositories \
    && apk update --no-cache \
    && apk upgrade --no-cache \  
    && apk add --no-cache --update \
    bash \
    skopeo \
    python3 \
    jq \
    py3-pip \
    tzdata \
    && cp /usr/share/zoneinfo/${TZ} /etc/localtime

COPY ./skopeoTransfer.py ./skopeolib.py ./toolbox.py ./getImage-proxy.sh ./getImage-hostnet.sh /app/

WORKDIR /app

ENTRYPOINT ["python3","skopeoTransfer.py"]