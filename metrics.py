# Copyright (c) 2024 Joel Torres
# Distributed under the MIT software license, see the accompanying
# file LICENSE or https://opensource.org/license/mit.

from prometheus_client import Counter, Gauge

PEER_C0NNECTIONS = Gauge("bitcoin_connections", "Number of peer connections", ["direction"])
NET_TOTAL_BYTES = Gauge("bitcoin_network_total_bytes", "Total of bytes received and sent", ["rxtx"])


metrics = {
    "connections": PEER_C0NNECTIONS,
    "net_total_bytes": NET_TOTAL_BYTES
}
