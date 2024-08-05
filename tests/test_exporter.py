# Copyright (c) 2024 Joel Torres
# Distributed under the MIT software license, see the accompanying
# file LICENSE or https://opensource.org/license/mit.

import pytest
from pathlib import Path
from bitcoin_exporter import BitcoinExporter, load_exporter_config
from blib.bitcoinpm import bitcoin_metrics
from blib.bitcoinrpc import BitcoinRpc
from blib.bitcoinutil import get_bitcoin_rpc_credentials


TEST_DATA = {
    "exporter_config_path": Path.joinpath(Path.cwd(), "test_data", "exporter.yaml"),
    "config_keys": {"port": 9001},
    "bitcoinrpc": BitcoinRpc(*get_bitcoin_rpc_credentials()),
    "metrics": bitcoin_metrics,
    "fetch_attr": ["uptime", "blockchain_info", "network_info", "net_totals", "memory_info", "mem_pool_info"],
    "stats_attr": ["exporter_rpc_total", "exporter_rpc_success", "exporter_rpc_error"]
}


def test_bitcoin_exporter_fetch():
    exporter = BitcoinExporter(TEST_DATA["bitcoinrpc"], TEST_DATA["metrics"])
    exporter._fetch_metricts()
    for attr in TEST_DATA["fetch_attr"]:
        assert eval("exporter.{}".format(attr))["error"] == None

    for attr in TEST_DATA["stats_attr"][:2]:
        assert eval("exporter.{}._value.get()".format(attr)) == len(TEST_DATA["fetch_attr"])
    assert eval("exporter.{}._value.get()".format(TEST_DATA["stats_attr"][-1])) == 0


def test_load_exporter_config():
    config = load_exporter_config(TEST_DATA["exporter_config_path"])
    for key in TEST_DATA["config_keys"]:
        assert config[key] == TEST_DATA["config_keys"][key]

