FROM alpine:3.6

ENV NGINX_VERSION 1.16.1-r6
ENV NJS_VERSION   0.4.0
ENV PKG_RELEASE   1

RUN apk update && \
    apk add --no-cache nginx=${NGINX_VERSION}
