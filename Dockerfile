FROM python:3.12-alpine3.23
LABEL maintainer="vovakucin082@gmail.com"

ENV PYTHOUNUNBUFFERED 1

RUN adduser \
    --disabled-password \
    --no-create-home \
    my_user

WORKDIR app/

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

RUN mkdir -p /app/files/media

RUN chown -R my_user:my_user /app

USER my_user
