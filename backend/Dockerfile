FROM python:3.7-alpine

ENV HOME=/usr/src/app
ENV APP_HOME=$HOME/web
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR $APP_HOME

RUN apk update apk upgrade && \
    apk add zlib-dev jpeg-dev postgresql-dev gcc python3-dev musl-dev && \
    apk add --update alpine-sdk && apk add libffi-dev openssl-dev cargo rust

RUN pip install --upgrade pip

COPY . .

RUN pip install -r requirements.txt

ENTRYPOINT ["/usr/src/app/web/docker-entrypoint.sh"]