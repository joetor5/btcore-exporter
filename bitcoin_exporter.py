#!/usr/bin/env python3
# Copyright (c) 2024-2025 Joel Torres
# Distributed under the MIT License. See the accompanying file LICENSE.

import os
import time
import signal
import sys
import argparse
import traceback
from pathlib import Path
from collections import deque
import yaml
import logging
from logging.handlers import RotatingFileHandler
from prometheus_client import start_http_server, Gauge
from btcorerpc.rpc import BitcoinRpc
from btcoreutil import *

__version__ = "0.1.5"

APP_ENV_HOME = os.getenv("BTCORE_HOME")
APP_HOME = Path(APP_ENV_HOME) if APP_ENV_HOME else Path.home()
APP_DIR = APP_HOME / ".btcore"
APP_DIR.mkdir(exist_ok=True)

APP_CONFIG = APP_DIR / "exporter.yaml"

LOG_MAX_BYTES = 10000000
LOG_MAX_BACKUP = 3

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

logger_format = logging.Formatter("%(asctime)s [%(name)s] %(levelname)s - %(message)s")
logger_file_handler = RotatingFileHandler(APP_DIR / "exporter.log", maxBytes=LOG_MAX_BYTES, backupCount=LOG_MAX_BACKUP)
logger_file_handler.setFormatter(logger_format)
logger_console_handler = logging.StreamHandler()
logger_console_handler.setFormatter(logger_format)

logger.addHandler(logger_file_handler)
logger.addHandler(logger_console_handler)

##### Prometheus Metrics #####

UPTIME = Gauge("bitcoin_uptime", "Total uptime of the node")

BLOCKCHAIN_INFO_BLOCKS = Gauge("bitcoin_blockchain_info_blocks", "Height of the most-work fully-validated chain")
BLOCKCHAIN_INFO_HEADERS = Gauge("bitcoin_blockchain_info_headers", "Number of headers that has been validated")
BLOCKCHAIN_INFO_DIFFICULTY = Gauge("bitcoin_blockchain_info_difficulty", "Current difficulty")
BLOCKCHAIN_INFO_TIME = Gauge("bitcoin_blockchain_info_time", "Block time")
BLOCKCHAIN_INFO_MEDIAN_TIME = Gauge("bitcoin_blockchain_info_median_time", "Median block time")
BLOCKCHAIN_INFO_VERIFICATION_PROGRESS = Gauge("bitcoin_blockchain_info_verification_progress", "Estimate of verification progress")
BLOCKCHAIN_INFO_SIZE_ON_DISK = Gauge("bitcoin_blockchain_info_size_on_disk", "Estimated size of the block and undo files on disk")

NETWORK_INFO_CONNECTIONS_IN = Gauge("bitcoin_network_info_connections_in", "Number of inbound connections")
NETWORK_INFO_CONNECTIONS_OUT = Gauge("bitcoin_network_info_connections_out", "Number of outbound connections")
NETWORK_INFO_CONNECTIONS = Gauge("bitcoin_network_info_connections", "Total number of connections")
NET_TOTALS_TOTAL_BYTES_RECV = Gauge("bitcoin_net_totals_total_bytes_recv", "Total bytes received")
NET_TOTALS_TOTAL_BYTES_SENT = Gauge("bitcoin_net_totals_total_bytes_sent", "Total bytes sent")

MEM_POOL_INFO_SIZE = Gauge("bitcoin_mem_pool_info_size", "Current TX count for the mempool")
MEM_POOL_INFO_BYTES = Gauge("bitcoin_mem_pool_info_bytes", "Sum of all virtual transaction sizes for the mempool")
MEM_POOL_INFO_USAGE = Gauge("bitcoin_mem_pool_info_usage", "Total memory usage for the mempool")
MEMORY_INFO_USED = Gauge("bitcoin_memory_info_used", "Number of bytes used")
MEMORY_INFO_FREE = Gauge("bitcoin_memory_info_free", "Number of bytes available in current arenas")
MEMORY_INFO_TOTAL = Gauge("bitcoin_memory_info_total", "Total number of bytes managed")
MEMORY_INFO_LOCKED = Gauge("bitcoin_memory_info_locked", "Amount of bytes that succeeded locking")
MEMORY_INFO_CHUNKS_USED = Gauge("bitcoin_memory_info_chunks_used", "Number allocated chunks")
MEMORY_INFO_CHUNKS_FREE = Gauge("bitcoin_memory_info_chunks_free", "Number unused chunks")


bitcoin_metrics = {
    "uptime": UPTIME,
    "blockchain_info_blocks": BLOCKCHAIN_INFO_BLOCKS,
    "blockchain_info_headers": BLOCKCHAIN_INFO_HEADERS,
    "blockchain_info_difficulty": BLOCKCHAIN_INFO_DIFFICULTY,
    "blockchain_info_time": BLOCKCHAIN_INFO_TIME,
    "blockchain_info_median_time": BLOCKCHAIN_INFO_MEDIAN_TIME,
    "blockchain_info_verification_progress": BLOCKCHAIN_INFO_VERIFICATION_PROGRESS,
    "blockchain_info_size_on_disk": BLOCKCHAIN_INFO_SIZE_ON_DISK,
    "network_info_connections_in": NETWORK_INFO_CONNECTIONS_IN,
    "network_info_connections_out": NETWORK_INFO_CONNECTIONS_OUT,
    "network_info_connections": NETWORK_INFO_CONNECTIONS,
    "net_totals_total_bytes_recv": NET_TOTALS_TOTAL_BYTES_RECV,
    "net_totals_total_bytes_sent": NET_TOTALS_TOTAL_BYTES_SENT,
    "mem_pool_info_size": MEM_POOL_INFO_SIZE,
    "mem_pool_info_bytes": MEM_POOL_INFO_BYTES,
    "mem_pool_info_usage": MEM_POOL_INFO_USAGE,
    "memory_info_used": MEMORY_INFO_USED,
    "memory_info_free": MEMORY_INFO_FREE,
    "memory_info_total": MEMORY_INFO_TOTAL,
    "memory_info_locked": MEMORY_INFO_LOCKED,
    "memory_info_chunks_used": MEMORY_INFO_CHUNKS_USED,
    "memory_info_chunks_free": MEMORY_INFO_CHUNKS_FREE
}

##############################

class BitcoinExporter:
    
    def __init__(self, rpc_obj: BitcoinRpc, metrics: dict):
        self.bitcoin_rpc = rpc_obj
        self.metrics = metrics
        self.errors_q = deque()
        self.exporter_rpc_fetch_time = Gauge("bitcoin_exporter_fetch_time", "Time elapsed for all rpc calls")
        self.exporter_rpc_total = Gauge("bitcoin_exporter_rpc_total", "Total of RPC calls")
        self.exporter_rpc_success = Gauge("bitcoin_exporter_rpc_success", "Total of RPC success calls")
        self.exporter_rpc_error = Gauge("bitcoin_exporter_rpc_error", "Total of RPC error calls")

    def _fetch_metricts(self):
        logger.info("Starting Exporter RPC metrics fetch")
        start_time = time.time()

        self.uptime = self.bitcoin_rpc.uptime()
        self.blockchain_info = self.bitcoin_rpc.get_blockchain_info()
        self.network_info = self.bitcoin_rpc.get_network_info()
        self.net_totals = self.bitcoin_rpc.get_net_totals()
        self.memory_info = self.bitcoin_rpc.get_memory_info()
        self.mem_pool_info = self.bitcoin_rpc.get_mem_pool_info()

        end_time = time.time()
        elapsed_time = end_time - start_time
        logger.info("Exporter RPC metrics fetch done, time elapsed: {}".format(elapsed_time))
        self.exporter_rpc_fetch_time.set(elapsed_time)

        self._update_rpc_stats()

    def _update_rpc_stats(self):
        self.exporter_rpc_total.set(self.bitcoin_rpc.get_rpc_total_count())
        self.exporter_rpc_success.set(self.bitcoin_rpc.get_rpc_success_count())
        self.exporter_rpc_error.set(self.bitcoin_rpc.get_rpc_error_count())

    def _check_error(self, metric):
        if not metric["error"]:
            return False
        else:
            self.errors_q.append(metric)
            return True

    def update_metrics(self):
        self._fetch_metricts()

        logger.info("Checking for RPC errors and updating metrics")

        if not self._check_error(self.uptime):
            self.metrics["uptime"].set(self.uptime["result"])
        
        if not self._check_error(self.blockchain_info):
            self.blockchain_info = self.blockchain_info["result"]
            self.metrics["blockchain_info_blocks"].set(self.blockchain_info["blocks"])
            self.metrics["blockchain_info_headers"].set(self.blockchain_info["headers"])
            self.metrics["blockchain_info_difficulty"].set(self.blockchain_info["difficulty"])
            self.metrics["blockchain_info_time"].set(self.blockchain_info["time"])
            self.metrics["blockchain_info_median_time"].set(self.blockchain_info["mediantime"])
            self.metrics["blockchain_info_verification_progress"].set(self.blockchain_info["verificationprogress"])
            self.metrics["blockchain_info_size_on_disk"].set(self.blockchain_info["size_on_disk"])

        if not self._check_error(self.network_info):
            self.network_info = self.network_info["result"]
            self.metrics["network_info_connections_in"].set(self.network_info["connections_in"])
            self.metrics["network_info_connections_out"].set(self.network_info["connections_out"])
            self.metrics["network_info_connections"].set(self.network_info["connections"])

        if not self._check_error(self.net_totals):
            self.net_totals = self.net_totals["result"]
            self.metrics["net_totals_total_bytes_recv"].set(self.net_totals["totalbytesrecv"])
            self.metrics["net_totals_total_bytes_sent"].set(self.net_totals["totalbytessent"])

        if not self._check_error(self.memory_info):
            self.memory_info = self.memory_info["result"]
            self.metrics["memory_info_used"].set(self.memory_info["locked"]["used"])
            self.metrics["memory_info_free"].set(self.memory_info["locked"]["free"])
            self.metrics["memory_info_total"].set(self.memory_info["locked"]["total"])

        if not self._check_error(self.mem_pool_info):
            self.mem_pool_info = self.mem_pool_info["result"]
            self.metrics["mem_pool_info_size"].set(self.mem_pool_info["size"])
            self.metrics["mem_pool_info_bytes"].set(self.mem_pool_info["bytes"])
            self.metrics["mem_pool_info_usage"].set(self.mem_pool_info["usage"])

        if self.errors_q:
            while self.errors_q:
                error_update = self.errors_q.popleft()
                rpc_id = error_update["id"]
                message = error_update["error"]["message"]
                logger.error("Got error from RPC: rpc_id={}, message: {}".format(rpc_id, message))


def load_exporter_config(config_path: Path = APP_CONFIG) -> dict:
    try:
        with open(config_path) as f:
            return yaml.safe_load(f) or {}
    except (FileNotFoundError, IsADirectoryError, PermissionError):
        logger.warning(f"Exporter config not found or unable to read ({APP_CONFIG}), other methods of configuration will be used")
    except yaml.YAMLError as e:
        logger.error(f"Error parsing YAML: {e}")

    return {}


def graceful_shutdown(signal_num, frame):
    logger.info("Stopping Bitcoin Core Exporter (signal={})".format(signal_num))
    frame.f_locals["server"].shutdown()
    frame.f_locals["t"].join()
    sys.exit(0)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--version", action="version", version=__version__)
    parser.add_argument("-p", "--port", type=int, help="Exporter HTTP server port")
    parser.add_argument("-r", "--rpc-ip", type=str, help="Bitcoin RPC IP")

    args = parser.parse_args()

    # Set defaults
    http_port = args.port if args.port else 8000
    bitcoin_host_ip = args.rpc_ip if args.rpc_ip else "127.0.0.1"

    # Update from configs if available
    exporter_config = load_exporter_config()

    if exporter_config:
        http_port = exporter_config.get("port", http_port)
        bitcoin_host_ip = exporter_config.get("host_ip", bitcoin_host_ip)

    try:
        rpc_user, rpc_password = get_bitcoin_rpc_credentials(custom_config=exporter_config)
    except BitcoinConfigError as e:
        print("\nError: {}, exporter can't start".format(e))
        logger.error(traceback.format_exc())
        sys.exit(1)

    bitcoin_rpc = BitcoinRpc(rpc_user, rpc_password, host_ip=bitcoin_host_ip)

    bitcoin_exporter = BitcoinExporter(bitcoin_rpc, bitcoin_metrics)

    # signal handling
    signal.signal(signal.SIGTERM, graceful_shutdown)
    signal.signal(signal.SIGINT, graceful_shutdown)

    server, t = start_http_server(http_port)
    logger.info("Starting Bitcoin Core Exporter v{} (pid={})".format(__version__, os.getpid()))
    while True:
        bitcoin_exporter.update_metrics()
        time.sleep(60)

if __name__ == "__main__":
    main()

