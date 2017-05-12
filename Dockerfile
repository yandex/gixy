FROM alpine:3.5

RUN apk add --no-cache python py-pip ca-certificates && \
    pip install --upgrade setuptools

ADD . /src

WORKDIR /src

RUN python setup.py install

ENTRYPOINT ["gixy"]