# Copyright (c) 2024 Joel Torres
# Distributed under the MIT software license, see the accompanying
# file LICENSE or https://opensource.org/license/mit.

import json
import requests
from pathlib import Path
import logging
from logging.handlers import RotatingFileHandler


CONNECTION_ERROR = 1
RPC_BAD_CREDENTIALS = 2

class BitcoinRpcError(Exception):
    pass

class BitcoinRpc:
    
    def __init__(self, rpc_user: str, rpc_password: str, host_ip: str = "127.0.0.1", host_port: int = 8332,
                 log_level=logging.INFO, log_dir: Path = Path.home(), log_bytes: int = 10000000, log_backup: int = 3):
        if rpc_user == "" or rpc_password == "":
            raise BitcoinRpcError("Empty credentials")

        self._log_file = "{}.log".format(__name__)
        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(log_level)
        self._logger_format = logging.Formatter("%(asctime)s [%(name)s] %(levelname)s - %(message)s")
        self._logger_handler = RotatingFileHandler(Path.joinpath(log_dir, self._log_file), maxBytes=log_bytes, backupCount=log_backup)
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
        self.rpc_success = 0
        self.rpc_errors = 0
    
    def _rpc_call(self, method: str, params: str = "") -> dict:
        self.rpc_id += 1
        self._logger.info("RPC call start: id={}, method={}".format(self.rpc_id, method))
        try:
            rpc_response = requests.post(self.rpc_url, auth=(self.rpc_user, self.rpc_password), headers=self.rpc_headers,
                                        json={"jsonrpc": self.rpc_version, "id": self.rpc_id,
                                            "method": method, "params": params.split()})
        except:
            return self._rpc_call_error(CONNECTION_ERROR, "failed to establish raw connection", "raw_connection")

        status_code = rpc_response.status_code
        response_text = rpc_response.text
        if status_code == 401 and response_text == "":
            return self._rpc_call_error(RPC_BAD_CREDENTIALS,
                                        "got empty payload and bad status code (possible wrong RPC credentials)",
                                        method)

        rpc_data = json.loads(response_text)
        rpc_data["method"] = method
        if rpc_response.ok:
            self.rpc_success += 1
            self._logger.info("RPC call success: id={}, status_code={}".format(self.rpc_id, status_code))
        else:
            self.rpc_errors += 1
            self._logger.error("RPC call error: id={}, status_code={}, message: {}".format(self.rpc_id, status_code, rpc_data["error"]["message"]))

        return rpc_data

    def _rpc_call_error(self, code, message, method):
        self.rpc_errors += 1
        self._logger.error("RPC call error: id={}, {}".format(self.rpc_id, message))
        return {"result": None,
                "error": {"code": code, "message": message},
                "id": self.rpc_id,
                "method": method}

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

    def get_rpc_total_count(self):
        return self.rpc_id

    def get_rpc_success_count(self):
        return self.rpc_success

    def get_rpc_error_count(self):
        return self.rpc_errors

