#!/bin/bash
# Copyright (c) 2024 Joel Torres
# Distributed under the MIT software license, see the accompanying
# file LICENSE or https://opensource.org/license/mit.

if [[ $SHELL == *"bash"* ]]; then
    SHRC=".bashrc"
elif [[ $SHELL == *"zsh"* ]]; then
    SHRC=".zshrc"
fi

EXPORTER_PY="$(pwd)/.venv/bin/python3"
EXPORTER_PATH="$(pwd)/bitcoin_exporter.py"
BOOT_SCRIPT=".bitcoin_exporter_boot.sh"
BOOT_SCRIPT_PATH="$HOME/$BOOT_SCRIPT"
CRON_JOB="@reboot $BOOT_SCRIPT_PATH"
CRON_TMP="crontab_tmp"

echo -e "#!$SHELL\n" > $BOOT_SCRIPT_PATH
echo ". $HOME/$SHRC" >> $BOOT_SCRIPT_PATH
echo -e "$EXPORTER_PY $EXPORTER_PATH &\n" >> $BOOT_SCRIPT_PATH
chmod +x $BOOT_SCRIPT_PATH
if [ -e $BOOT_SCRIPT_PATH ]; then
    echo "Boot script generated at $BOOT_SCRIPT_PATH"
else
    echo "Error generating boot script at $BOOT_SCRIPT_PATH"
    exit 1
fi

if [ $(crontab -l | grep "$BOOT_SCRIPT" >/dev/null 2>&1; echo $?) != 0 ]; then
    echo "Updating crontab..."
    crontab -l > $CRON_TMP
    echo $CRON_JOB >> $CRON_TMP
    crontab $CRON_TMP
    rm $CRON_TMP
fi
