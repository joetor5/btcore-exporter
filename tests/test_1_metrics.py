# Copyright (c) 2024 Joel Torres
# Distributed under the MIT software license, see the accompanying
# file LICENSE or https://opensource.org/license/mit.

from blib.bitcoinpm import bitcoin_metrics


TEST_DATA = {
    "uptime": [1102822, 1102882, 1102942],
    "blockchain_info_blocks": [854367, 854370, 854373],
    "blockchain_info_headers": [854367, 854370, 854373],
    "blockchain_info_difficulty": [82047728459932.75, 82047728459932.75, 82047728459932.75],
    "blockchain_info_time": [1722190090, 1722192236, 1722193424],
    "blockchain_info_median_time": [1722188318, 1722188801, 1722191929],
    "blockchain_info_verification_progress": [0.9999982735347266, 1, 0.9999966097248985],
    "blockchain_info_size_on_disk": [2120712243, 2126125527, 1975611474],
    "network_info_connections_in": [108, 106, 111],
    "network_info_connections_out": [10, 10, 10],
    "network_info_connections": [118, 116, 121],
    "net_totals_total_bytes_recv": [18846626913, 18847383678, 18848211087],
    "net_totals_total_bytes_sent": [35230942351, 35234321239, 35237839509],
    "mem_pool_info_size": [72075, 76090],
    "mem_pool_info_bytes": [41820037, 42572174],
    "mem_pool_info_usage": [207623152, 213855408],
    "memory_info_used": [3408, 3408],
    "memory_info_free": [258736, 258736],
    "memory_info_total": [262144, 262144],
    "memory_info_locked": [262144, 262144],
    "memory_info_chunks_used": [100, 100],
    "memory_info_chunks_free": [4, 4]
}


def test_values_init():
    for metric in bitcoin_metrics:
        assert bitcoin_metrics[metric]._value.get() == 0

def test_values_set():
    metric_keys = bitcoin_metrics.keys()
    tested_metrics = 0
    for metric in metric_keys:
        if metric not in TEST_DATA or not TEST_DATA[metric]:
            continue
        for value in TEST_DATA[metric]:
            bitcoin_metrics[metric].set(value)
            assert bitcoin_metrics[metric]._value.get() == value
        
        tested_metrics += 1
        
    assert tested_metrics == len(metric_keys)
