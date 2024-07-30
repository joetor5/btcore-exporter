# Copyright (c) 2024 Joel Torres
# Distributed under the MIT software license, see the accompanying
# file LICENSE or https://opensource.org/license/mit.

PY = python3
PIP = pip3
VENV_DIR = .venv
VENV_EXEC = $(VENV_DIR)/bin/activate
PROG = bitcoin-exporter.py

venv:
	$(PY) -m venv $(VENV_DIR) && . $(VENV_EXEC) && $(PIP) install -r requirements.txt

test:
	. $(VENV_EXEC) && $(PY) -m pytest .

run:
	. $(VENV_EXEC) && $(PY) $(PROG) &

clean:
	rm -rf $(VENV_DIR)
