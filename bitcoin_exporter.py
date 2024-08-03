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
from pathlib import Path
from collections import deque
import yaml
from prometheus_client import start_http_server
from blib.bitcoinrpc import BitcoinRpc
from blib.bitcoinpm import bitcoin_metrics
from blib.bitcoinutil import *

VERSION = "1.0-dev"
APP_DIR = Path.joinpath(Path.home(), ".bitcoinexporter")
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
        self.errors_q = deque()
        logger.info("Exporter initialized, metrics count={}".format(len(metrics.keys())))

    def _fetch_metricts(self):
        self.fetch_count += 1
        
        logger.info("Starting Bitcoin RPC fetch, count={}".format(self.fetch_count))

        self.uptime = self.bitcoin_rpc.uptime()
        self.blockchain_info = self.bitcoin_rpc.get_blockchain_info()
        self.network_info = self.bitcoin_rpc.get_network_info()
        self.net_totals = self.bitcoin_rpc.get_net_totals()
        self.memory_info = self.bitcoin_rpc.get_memory_info()
        self.mem_pool_info = self.bitcoin_rpc.get_mem_pool_info()

        logger.info("Bitcoin RPC fetch done")

    def update_metrics(self):
        self._fetch_metricts()

        logger.info("Checking for RPC errors and updating metrics")

        if not self.uptime["error"]:
            self.metrics["uptime"].set(self.uptime["result"])
        else:
            self.errors_q.append(self.uptime)
        
        if not self.blockchain_info["error"]:
            self.blockchain_info = self.blockchain_info["result"]
            self.metrics["blockchain_info_blocks"].set(self.blockchain_info["blocks"])
            self.metrics["blockchain_info_headers"].set(self.blockchain_info["headers"])
            self.metrics["blockchain_info_difficulty"].set(self.blockchain_info["difficulty"])
            self.metrics["blockchain_info_time"].set(self.blockchain_info["time"])
            self.metrics["blockchain_info_median_time"].set(self.blockchain_info["mediantime"])
            self.metrics["blockchain_info_verification_progress"].set(self.blockchain_info["verificationprogress"])
            self.metrics["blockchain_info_size_on_disk"].set(self.blockchain_info["size_on_disk"])
        else:
            self.errors_q.append(self.blockchain_info)

        if not self.network_info["error"]:
            self.network_info = self.network_info["result"]
            self.metrics["network_info_connections_in"].set(self.network_info["connections_in"])
            self.metrics["network_info_connections_out"].set(self.network_info["connections_out"])
            self.metrics["network_info_connections"].set(self.network_info["connections"])
        else:
            self.errors_q.append(self.network_info)

        if not self.net_totals["error"]:
            self.net_totals = self.net_totals["result"]
            self.metrics["net_totals_total_bytes_recv"].set(self.net_totals["totalbytesrecv"])
            self.metrics["net_totals_total_bytes_sent"].set(self.net_totals["totalbytessent"])
        else:
            self.errors_q.append(self.net_totals)

        if not self.mem_pool_info["error"]:
            self.mem_pool_info = self.mem_pool_info["result"]
            self.metrics["mem_pool_info_size"].set(self.mem_pool_info["size"])
            self.metrics["mem_pool_info_bytes"].set(self.mem_pool_info["bytes"])
            self.metrics["mem_pool_info_usage"].set(self.mem_pool_info["usage"])
        else:
            self.errors_q.append(self.mem_pool_info)

        if not self.memory_info["error"]:
            self.memory_info = self.memory_info["result"]
            self.metrics["memory_info_used"].set(self.memory_info["locked"]["used"])
            self.metrics["memory_info_free"].set(self.memory_info["locked"]["free"])
            self.metrics["memory_info_total"].set(self.memory_info["locked"]["total"])
        else:
            self.errors_q.append(self.memory_info)

        if self.errors_q:
            while self.errors_q:
                error_update = self.errors_q.pop()
                rpc_id = error_update["id"]
                method = error_update["method"]
                message = error_update["error"]["message"]
                logger.error("Got error from RPC: rpc_id={}, method={}, message: {}".format(rpc_id, method, message))


def load_exporter_config() -> dict:
    with open(APP_CONFIG) as f:
        return yaml.safe_load(f)

def graceful_shutdown(signal_num, frame):
    logger.info("Stopping Bitcoin Core Exporter (signal={})".format(signal_num))
    frame.f_locals["server"].shutdown()
    frame.f_locals["t"].join()
    sys.exit(0)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--version", action="version", version=VERSION)
    parser.add_argument("-p", "--port", type=int, help="Exporter HTTP server port")

    args = parser.parse_args()

    # defaults
    http_port = 8000

    # update from args
    if args.port:
        http_port = args.port

    # update from configs
    if APP_CONFIG.exists():
        exporter_config = load_exporter_config()
        if exporter_config:
            if "port" in exporter_config:
                http_port = exporter_config["port"]

    rpc_user, rpc_password = get_bitcoin_rpc_credentials()

    bitcoin_rpc = BitcoinRpc(rpc_user, rpc_password, log_dir=APP_DIR)
    bitcoin_exporter = BitcoinExporter(bitcoin_rpc, bitcoin_metrics)

    # signal handling
    signal.signal(signal.SIGTERM, graceful_shutdown)
    signal.signal(signal.SIGINT, graceful_shutdown)

    server, t = start_http_server(http_port)
    logger.info("Starting Bitcoin Core Exporter (pid={})".format(os.getpid()))
    while True:
        bitcoin_exporter.update_metrics()
        time.sleep(60)

if __name__ == "__main__":
    main()

