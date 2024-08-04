# Copyright (c) 2024 Joel Torres
# Distributed under the MIT software license, see the accompanying
# file LICENSE or https://opensource.org/license/mit.

import pytest
from pathlib import Path
from blib.bitcoinrpc import BitcoinRpc, BitcoinRpcError, CONNECTION_ERROR, RPC_BAD_CREDENTIALS
from blib.bitcoinutil import get_bitcoin_rpc_credentials

TEST_DATA = {
    "log_dir": Path.joinpath(Path.cwd(), "test_data"),
    "rpc_credentials": get_bitcoin_rpc_credentials(),
    "rpc_credentials_bad": ("test", "test123"),
    "bad_port": 9000,
    "methods": ["uptime", "get_blockchain_info", "get_network_info", "get_net_totals",
                "get_memory_info", "get_mem_pool_info"]
}

def test_rpc_call():
    rpc = BitcoinRpc(*TEST_DATA["rpc_credentials"], log_dir=TEST_DATA["log_dir"])
    for method in TEST_DATA["methods"]:
        response = eval("rpc.{}()".format(method))
        assert response["error"] == None

    assert rpc.get_rpc_total_count() == len(TEST_DATA["methods"])
    assert rpc.get_rpc_error_count() == 0
    assert rpc.get_rpc_success_count() == len(TEST_DATA["methods"])

def test_connection_error():
    rpc = BitcoinRpc(*TEST_DATA["rpc_credentials"], host_port=TEST_DATA["bad_port"],
                     log_dir=TEST_DATA["log_dir"])

    for method in TEST_DATA["methods"]:
        response = eval("rpc.{}()".format(method))
        assert response["result"] == None and \
               response["error"]["code"] == CONNECTION_ERROR and \
               response["error"]["message"] == "failed to establish raw connection"

    assert rpc.get_rpc_total_count() == len(TEST_DATA["methods"])
    assert rpc.get_rpc_error_count() == len(TEST_DATA["methods"])
    assert rpc.get_rpc_success_count() == 0

def test_rpc_empty_credentials():
    with pytest.raises(BitcoinRpcError):
        rpc = BitcoinRpc(rpc_user="", rpc_password="")

def test_rpc_bad_credentials():
    rpc = BitcoinRpc(*TEST_DATA["rpc_credentials_bad"], log_dir=TEST_DATA["log_dir"])
    response = rpc.uptime()
    assert response["result"] == None and \
           response["error"]["code"] == RPC_BAD_CREDENTIALS and \
           response["error"]["message"] == "got empty payload and bad status code (possible wrong RPC credentials)"

    assert rpc.get_rpc_total_count() == 1
    assert rpc.get_rpc_error_count() == 1
    assert rpc.get_rpc_success_count() == 0
