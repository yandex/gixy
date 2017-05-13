FROM python:2.7-alpine

ADD . /src

WORKDIR /src

RUN python2 setup.py install

ENTRYPOINT ["gixy"]
