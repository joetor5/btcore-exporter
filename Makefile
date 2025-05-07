# Copyright (c) 2024-2025 Joel Torres
# Distributed under the MIT License. See the accompanying file LICENSE.

PY = python3
PIP = pip3
VENV_DIR = .venv
VENV_EXEC = $(VENV_DIR)/bin/activate
PROG = bitcoin_exporter.py

venv:
	$(PY) -m venv $(VENV_DIR) && . $(VENV_EXEC) && $(PIP) install --upgrade pip && $(PIP) install -r requirements.txt

test:
	. $(VENV_EXEC) && $(PY) -m pytest .

run:
	. $(VENV_EXEC) && $(PY) $(PROG) >/dev/null 2>&1 &

clean:
	rm -rf $(VENV_DIR)

boot:
	bash boot.sh

stop:
	pkill -f bitcoin_exporter
