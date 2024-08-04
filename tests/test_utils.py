# Copyright (c) 2024 Joel Torres
# Distributed under the MIT software license, see the accompanying
# file LICENSE or https://opensource.org/license/mit.

import pytest
import os
from pathlib import Path
from blib.bitcoinutil import *


TEST_DATA = {
    "data_path": Path.joinpath(Path.cwd(), "test_data"),
    "data_path_bad": Path.joinpath(Path.cwd(), "tests"),
    "rpcuser_conf": "test",
    "rpcpassword_conf": "FEAFDCnkAakUZMbv71BZV82/qi3zcspQYLLjHay9lnI=",
    "rpcuser_env": "rpctest123",
    "rpcpassword_env": "rpctest123"
}


def test_load_bitcoin_config():
    config = load_bitcoin_config(TEST_DATA["data_path"])
    assert config["server"] == "1"
    assert config["rpcuser"] == TEST_DATA["rpcuser_conf"]
    assert config["rpcpassword"] == TEST_DATA["rpcpassword_conf"]
    assert "# rpcuser" not in config
    assert "# rpcpassword" not in config

def test_get_bitcoin_rpc_credentials_env():
    env_user = TEST_DATA["rpcuser_env"]
    env_password = TEST_DATA["rpcpassword_env"]
    os.environ["BITCOIN_RPC_USER"] = env_user
    os.environ["BITCOIN_RPC_PASSWORD"] = env_password

    rpcuser, rpcpassword = get_bitcoin_rpc_credentials()
    assert rpcuser == env_user
    assert rpcpassword == env_password

def test_get_bitcoin_rpc_credentials_conf():
    del os.environ["BITCOIN_RPC_USER"]
    del os.environ["BITCOIN_RPC_PASSWORD"]

    rpcuser, rpcpassword = get_bitcoin_rpc_credentials(TEST_DATA["data_path"])
    assert rpcuser == TEST_DATA["rpcuser_conf"]
    assert rpcpassword == TEST_DATA["rpcpassword_conf"]

def test_get_bitcoin_rpc_credentials_error():
    with pytest.raises(BitcoinConfigError):
        rpcuser, rpcpassword = get_bitcoin_rpc_credentials(TEST_DATA["data_path_bad"])
