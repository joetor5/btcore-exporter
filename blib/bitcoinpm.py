# Copyright (c) 2024 Joel Torres
# Distributed under the MIT software license, see the accompanying
# file LICENSE or https://opensource.org/license/mit.

from prometheus_client import Counter, Gauge


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
