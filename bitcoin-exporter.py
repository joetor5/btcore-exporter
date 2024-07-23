#!/usr/bin/env python3
# Copyright (c) 2024 Joel Torres
# Distributed under the MIT software license, see the accompanying
# file LICENSE or https://opensource.org/license/mit.

import os
import time
import logging
import signal
import sys
import argparse
import platform
from pathlib import Path
import yaml
from prometheus_client import start_http_server
from bitcoinrpc import BitcoinRpc
from metrics import metrics

HOME_DIR = Path.home()
PLATFORM_OS = platform.system()
if PLATFORM_OS == "Linux":
    BITCOIN_DIR = Path.joinpath(HOME_DIR, ".bitcoin")
elif PLATFORM_OS == "Darwin":
    BITCOIN_DIR = Path.joinpath(HOME_DIR, "Library", "Application Support", "Bitcoin")

APP_DIR = Path.joinpath(HOME_DIR, ".bitcoinexporter")
if not APP_DIR.exists():
    APP_DIR.mkdir()
APP_CONFIG = Path.joinpath(APP_DIR, "exporter.yaml")

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger_format = logging.Formatter("%(asctime)s [%(name)s] %(levelname)s - %(message)s")
logger_handler = logging.FileHandler(Path.joinpath(APP_DIR, "exporter.log"))
logger_handler.setFormatter(logger_format)
logger.addHandler(logger_handler)


class BitcoinExporter:
    
    def __init__(self, rpc_obj: BitcoinRpc, metrics: dict):
        self.bitcoin_rpc = rpc_obj
        self.metrics = metrics
        self.fetch_count = 0
        logger.info("Exporter initialized, metrics count={}".format(len(metrics.keys())))

    def _fetch_metricts(self):
        self.fetch_count += 1
        
        logger.info("Starting metrics fetch, count={}".format(self.fetch_count))
        self.uptime = self.bitcoin_rpc.uptime()
        self.network_info = self.bitcoin_rpc.get_network_info()
        self.net_totals = self.bitcoin_rpc.get_net_totals()
        self.memory_info = self.bitcoin_rpc.get_memory_info()
        self.mem_pool_info = self.bitcoin_rpc.get_mem_pool_info()

    def update_metrics(self):
        self._fetch_metricts()

        logger.info("Updating metrics")
        self.metrics["uptime"].set(self.uptime)
        
        self.metrics["network_info_connections_in"].set(self.network_info["connections_in"])
        self.metrics["network_info_connections_out"].set(self.network_info["connections_out"])
        self.metrics["network_info_connections"].set(self.network_info["connections"])
        self.metrics["net_totals_total_bytes_recv"].set(self.net_totals["totalbytesrecv"])
        self.metrics["net_totals_total_bytes_sent"].set(self.net_totals["totalbytessent"])

        self.metrics["mem_pool_info_size"].set(self.mem_pool_info["size"])
        self.metrics["mem_pool_info_bytes"].set(self.mem_pool_info["bytes"])
        self.metrics["mem_pool_info_usage"].set(self.mem_pool_info["usage"])
        self.metrics["memory_info_used"].set(self.memory_info["locked"]["used"])
        self.metrics["memory_info_free"].set(self.memory_info["locked"]["free"])
        self.metrics["memory_info_total"].set(self.memory_info["locked"]["total"])

def load_bitcoin_config() -> dict:
    config_file = Path.joinpath(BITCOIN_DIR, "bitcoin.conf")
    config = {}
    if config_file.exists():
        with open(config_file) as f:
            for line in f:
                if "=" in line:
                    key, val = line.split("=")
                    config[key] = val.strip()
    
    return config
    
def get_bitcoin_rpc_credentials() -> tuple:
    # get from env variables
    rpc_user = os.getenv("BITCOIN_RPC_USER")
    rpc_password = os.getenv("BITCOIN_RPC_PASSWORD")
    if rpc_user and rpc_password:
        logger.info("Got RPC credentials from env vars")
        return rpc_user, rpc_password

    # get from bitcoin.conf
    config = load_bitcoin_config()
    if config:
        if "rpcuser" in config and "rpcpassword" in config:
            logger.info("Got RPC credentials from bitcoin.conf")
            return config["rpcuser"], config["rpcpassword"]

def graceful_shutdown(signal_num, frame):
    logger.info("Stopping Bitcoin Core Exporter (signal={})".format(signal_num))
    frame.f_locals["server"].shutdown()
    frame.f_locals["t"].join()
    sys.exit(0)


def main():
    rpc_user, rpc_password = get_bitcoin_rpc_credentials()

    bitcoin_rpc = BitcoinRpc(rpc_user, rpc_password, log_dir=APP_DIR)
    bitcoin_exporter = BitcoinExporter(bitcoin_rpc, metrics)

    # signal handling
    signal.signal(signal.SIGTERM, graceful_shutdown)
    signal.signal(signal.SIGINT, graceful_shutdown)

    server, t = start_http_server(8000)
    logger.info("Starting Bitcoin Core Exporter (pid={})".format(os.getpid()))
    while True:
        bitcoin_exporter.update_metrics()
        time.sleep(60)

if __name__ == "__main__":
    main()

