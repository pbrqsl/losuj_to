FROM python:3.12-alpine

ENV PYTHONUNBUFFERED=1
WORKDIR /losuj_to/



# RUN \
#  apk add --no-cache postgresql-libs && \
#  apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev && \
#  python3 -m pip install -r requirements.txt --no-cache-dir && \
#  apk --purge del .build-deps

RUN \
 apk add --no-cache postgresql-libs && \
 apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev


COPY requirements.txt .
RUN \
 python3 -m pip install -r requirements.txt --no-cache-dir

RUN \
 apk add --no-cache postgresql-client


#COPY losuj_to/init_django.sh .

RUN \
 apk --purge del .build-deps

COPY losuj_to/ .

COPY losuj_to/init_django.sh .
