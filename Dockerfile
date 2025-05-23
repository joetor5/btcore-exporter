# Copyright (c) 2024-2025 Joel Torres
# Distributed under the MIT License. See the accompanying file LICENSE.

FROM python:alpine

WORKDIR /opt
ENV BTCORE_HOME=/opt
ENV BTCORERPC_LOG=1
ENV BTCORERPC_LOG_CONSOLE=1

COPY bitcoin_exporter.py requirements.txt /opt/
RUN pip install -r /opt/requirements.txt
RUN mkdir /opt/.btcore

ENTRYPOINT [ "python", "bitcoin_exporter.py" ]
