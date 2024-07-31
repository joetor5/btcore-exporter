#!/bin/bash
# Copyright (c) 2024 Joel Torres
# Distributed under the MIT software license, see the accompanying
# file LICENSE or https://opensource.org/license/mit.

if [[ $SHELL == *"bash"* ]]; then
    SHRC="$HOME/.bashrc"
elif [[ $SHELL == *"zsh"* ]]; then
    SHRC="$HOME/.zshrc"
fi

EXPORTER_PY="$(pwd)/.venv/bin/python3"
EXPORTER_PATH="$(pwd)/bitcoin-exporter.py"
CRON_JOB='@reboot . '"$SHRC"' && $BITCOIN_EXPORTER_PY $BITCOIN_EXPORTER_PATH'


if [ $(grep BITCOIN_EXPORTER_PY $SHRC >/dev/null; echo $?) != 0 ]; then
    echo "BITCOIN_EXPORTER_PY: $EXPORTER_PY >> $SHRC"
    echo "export BITCOIN_EXPORTER_PY=\"$EXPORTER_PY\"" >> $SHRC
fi

if [ $(grep BITCOIN_EXPORTER_PATH $SHRC >/dev/null; echo $?) != 0 ]; then
    echo "BITCOIN_EXPORTER_PATH: $EXPORTER_PATH >> $SHRC"
    echo "export BITCOIN_EXPORTER_PATH=\"$EXPORTER_PATH\"" >> $SHRC
fi

crontab -l | grep "BITCOIN_EXPORTER_PY\|BITCOIN_EXPORTER_PATH" > /dev/null
if [ $? != 0 ]; then
    echo "CRON_JOB: $CRON_JOB"
    crontab -l > crontab_tmp
    echo $CRON_JOB >> crontab_tmp
    crontab crontab_tmp
    rm crontab_tmp
fi
