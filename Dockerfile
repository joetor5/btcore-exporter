# Copyright (c) 2024 Joel Torres
# Distributed under the MIT License. See the accompanying file LICENSE.

FROM python:alpine

WORKDIR /opt
ENV BITCOIN_EXPORTER_HOME=/opt

COPY . /opt/
RUN pip install -r /opt/requirements.txt
RUN mkdir /opt/.bitcoinexporter

ENTRYPOINT [ "python", "bitcoin_exporter.py" ]
