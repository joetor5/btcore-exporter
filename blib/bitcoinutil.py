# Copyright (c) 2024 Joel Torres
# Distributed under the MIT License. See the accompanying file LICENSE.

import os
import platform
from pathlib import Path


if platform.system() == "Linux":
    BITCOIN_DIR = Path.home() / ".bitcoin"
elif platform.system() == "Darwin":
    BITCOIN_DIR = Path.home() / "Library" / "Application Support" / "Bitcoin"


class BitcoinConfigError(Exception):
    pass

def load_bitcoin_config(config_path: Path = BITCOIN_DIR) -> dict:
    config_file = config_path / "bitcoin.conf"
    config = {}

    if config_file.exists():
        with config_file.open() as f:
            for line in f:
                line = line.strip()
                if line.startswith("#") or "=" not in line:
                    continue

                key, val = line.split("=", 1)
                config[key.strip()] = val.strip()

    return config

def get_bitcoin_rpc_credentials(bitcoin_config: Path = BITCOIN_DIR, custom_config: dict = None) -> tuple:
    # Check environment variables first
    rpc_user = os.getenv("BITCOIN_RPC_USER")
    rpc_password = os.getenv("BITCOIN_RPC_PASSWORD")

    if rpc_user and rpc_password:
        return rpc_user, rpc_password

    # Load credentials from bitcoin.conf
    config = load_bitcoin_config(bitcoin_config)
    rpc_user = config.get("rpcuser")
    rpc_password = config.get("rpcpassword")

    if rpc_user and rpc_password:
        return rpc_user, rpc_password

    # Check custom config
    rpc_user = custom_config.get("rpc_user") if custom_config else None
    rpc_password = custom_config.get("rpc_password") if custom_config else None

    if rpc_user and rpc_password:
        return rpc_user, rpc_password
    
    # If all methods fail, raise an error
    raise BitcoinConfigError("Unable to get bitcoin RPC credentials")

