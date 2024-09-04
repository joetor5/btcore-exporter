# Copyright (c) 2024 Joel Torres
# Distributed under the MIT software license, see the accompanying
# file LICENSE or https://opensource.org/license/mit.

FROM python:alpine

WORKDIR /opt
ENV BITCOIN_EXPORTER_HOME=/opt

COPY . /opt/
RUN pip install -r /opt/requirements.txt
RUN mkdir /opt/.bitcoinexporter

ENTRYPOINT [ "python", "bitcoin_exporter.py" ]
