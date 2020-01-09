FROM python:alpine

ADD . /src

WORKDIR /src

RUN python3 setup.py install

ENTRYPOINT ["gixy"]
