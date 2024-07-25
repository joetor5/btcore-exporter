# Copyright (c) 2024 Joel Torres
# Distributed under the MIT software license, see the accompanying
# file LICENSE or https://opensource.org/license/mit.

import logging
import json
from pathlib import Path
import requests


class BitcoinRpc:
    
    def __init__(self, rpc_user, rpc_password, host_ip="127.0.0.1", host_port=8332,
                 log_level=logging.INFO, log_dir: Path = Path.home()):
        
        self._log_file = "{}.log".format(__name__)
        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(log_level)
        self._logger_format = logging.Formatter("%(asctime)s [%(name)s] %(levelname)s - %(message)s")
        self._logger_handler = logging.FileHandler(Path.joinpath(log_dir, self._log_file))
        self._logger_handler.setFormatter(self._logger_format)
        self._logger.addHandler(self._logger_handler)

        self.rpc_version = "1.0"
        self.rpc_user = rpc_user
        self.rpc_password = rpc_password
        self.host_ip = host_ip
        self.host_port = host_port
        self.rpc_url = "http://{ip}:{port}".format(ip=self.host_ip, port=self.host_port)
        self.rpc_headers = {
            "Content-Type": "text/plain"
        }
        self.rpc_id = 0

    def __repr__(self) -> str:
        return "{cname}({user}, {passw}, {ip}, {port})".format(cname=self.__class__.__name__, 
                                                               user=self.rpc_user, passw=self.rpc_password,
                                                               ip=self.host_ip, port=self.host_port)
    
    def __str__(self) -> str:
        pass
    
    def _rpc_call(self, method: str, params: str = "") -> dict:
        self.rpc_id += 1
        self._logger.info("RPC call start: id={}, method={}".format(self.rpc_id, method))
        rpc_response = requests.post(self.rpc_url, auth=(self.rpc_user, self.rpc_password), headers=self.rpc_headers, 
                                     json={"jsonrpc": self.rpc_version, "id": self.rpc_id, 
                                           "method": method, "params": params.split()})
        
        if rpc_response.ok:
            return json.loads(rpc_response.text)["result"]

    def uptime(self) -> dict:
        """Returns the total uptime of the server."""
        return self._rpc_call("uptime")
    
    def get_blockchain_info(self) -> dict:
        """Returns various state info regarding blockchain processing."""
        return self._rpc_call("getblockchaininfo")
    
    def get_block_count(self) -> dict:
        """Returns the height of the most-work fully-validated chain."""
        return self._rpc_call("getblockcount")
    
    def get_memory_info(self) -> dict:
        """Returns information about memory usage."""
        return self._rpc_call("getmemoryinfo")
    
    def get_mem_pool_info(self) -> dict:
        """Returns details on the active state of the TX memory pool"""
        return self._rpc_call("getmempoolinfo")

    def get_network_info(self) -> dict:
        """Returns various state info regarding P2P networking."""
        return self._rpc_call("getnetworkinfo")
    
    def get_connection_count(self) -> dict:
        """Returns the number of connections to other nodes."""
        return self._rpc_call("getconnectioncount")
    
    def get_net_totals(self) -> dict:
        """Returns information about network traffic"""
        return self._rpc_call("getnettotals")
    
    def get_node_addresses(self, count: int = 0) -> dict:
        if count < 0:
            count = 0
        return self._rpc_call("getnodeaddresses", str(count))
    
