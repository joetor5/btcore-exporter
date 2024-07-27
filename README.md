# bitcoin-core-exporter

Simple [Prometheus](https://prometheus.io/) exporter for exposing various metrics from a full [Bitcoin Core](https://bitcoincore.org/) node.

## Setup

1. Clone the repo on the same machine where the Bitcoin Core node is running.
```
git clone https://github.com/joetor5/bitcoin-core-exporter.git
cd bitcoin-core-exporter
```
2. Create a Python venv and install dependencies
```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
3. Start the exporter
```
chmod +x bitcoin-exporter.py
./bitcoin-exporter.py &
```

This will start the exporter http server on port 8000 and collect metrics every 60 seconds. You can select a different port with the -p arg. Run with -h arg for general usage and options.

4. View all the metrics (starting with bitcoin_)
```
curl http://localhost:8000/metrics
```
5. Modify the prometheus.yml config for pulling these metrics from the exporter
```
scrape_configs:

  - job_name: "bitcoin-core"
    scrape_interval: 60s
    static_configs:
      - targets: ["localhost:8000"]

```
