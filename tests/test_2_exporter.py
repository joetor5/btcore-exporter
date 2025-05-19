# Copyright (c) 2024-2025 Joel Torres
# Distributed under the MIT License. See the accompanying file LICENSE.

import os
from pathlib import Path
from bitcoin_exporter import BitcoinExporter, bitcoin_metrics, load_exporter_config
from btcorerpc.rpc import BitcoinRpc
from btcoreutil import get_bitcoin_rpc_credentials


TEST_DATA = {
    "exporter_config_path": Path.joinpath(Path.cwd(), "tests", "data", "exporter.yaml"),
    "config_keys": {"port": 9001},
    "bitcoinrpc": BitcoinRpc(*get_bitcoin_rpc_credentials(), host_ip=os.getenv("BITCOIN_RPC_IP"), raw_json_response=True),
    "metrics": bitcoin_metrics,
    "fetch_attr": ["uptime", "blockchain_info", "network_info", "net_totals", "memory_info", "mem_pool_info"],
    "stats_attr": ["exporter_rpc_total", "exporter_rpc_success", "exporter_rpc_error"]
}


def test_bitcoin_exporter():
    exporter = BitcoinExporter(TEST_DATA["bitcoinrpc"], TEST_DATA["metrics"])
    exporter._fetch_metricts()
    for attr in TEST_DATA["fetch_attr"]:
        assert eval("exporter.{}".format(attr))["error"] == None

    exporter.update_metrics()

    for attr in TEST_DATA["stats_attr"][:2]:
        assert eval("exporter.{}._value.get()".format(attr)) == len(TEST_DATA["fetch_attr"]) * 2
    assert eval("exporter.{}._value.get()".format(TEST_DATA["stats_attr"][-1])) == 0

    assert bitcoin_metrics["uptime"]._value.get() == exporter.uptime["result"]
    assert bitcoin_metrics["network_info_connections_in"]._value.get() == exporter.network_info["connections_in"]
    assert bitcoin_metrics["blockchain_info_blocks"]._value.get() == exporter.blockchain_info["blocks"]
    assert bitcoin_metrics["net_totals_total_bytes_sent"]._value.get() == exporter.net_totals["totalbytessent"]
    assert bitcoin_metrics["memory_info_used"]._value.get() == exporter.memory_info["locked"]["used"]
    assert bitcoin_metrics["mem_pool_info_usage"]._value.get() == exporter.mem_pool_info["usage"]

    assert not exporter.errors_q


def test_load_exporter_config():
    config = load_exporter_config(TEST_DATA["exporter_config_path"])
    for key in TEST_DATA["config_keys"]:
        assert config[key] == TEST_DATA["config_keys"][key]

