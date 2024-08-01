# Copyright (c) 2024 Joel Torres
# Distributed under the MIT software license, see the accompanying
# file LICENSE or https://opensource.org/license/mit.

from bitcoinrpc import BitcoinRpc, CONNECTION_ERROR
from bitcoin_exporter import get_bitcoin_rpc_credentials

TEST_DATA = {
    "rpc_credentials": get_bitcoin_rpc_credentials(),
    "rpc_credentials_bad": ("test", "test123"),
    "bad_port": 9000
}

def test_connection_error():
    rpc = BitcoinRpc(*TEST_DATA["rpc_credentials"], host_port=TEST_DATA["bad_port"])
    response = rpc.uptime()
    assert response["result"] == None and response["error"]["code"] == CONNECTION_ERROR and response["error"]["message"] == "Failed to establish raw connection"
