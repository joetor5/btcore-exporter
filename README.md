# btcore-exporter

Simple [Prometheus](https://prometheus.io/) exporter for exposing various metrics from a full [Bitcoin Core](https://bitcoincore.org/) node.

Works on macOS and GNU/Linux systems.

## Table of Contents

- [License](#license)
- [Installing](#installing)
  - [Manual Setup](#manual-setup)
  - [Make Setup](#make-setup)
  - [Docker Setup](#docker-setup)

## License

Distributed under the MIT License. See the accompanying file [LICENSE](https://github.com/joetor5/btcore-exporter/blob/main/LICENSE).

## Installing

### Manual Setup

:hammer:

:one: **Clone the repo on the same machine where the Bitcoin Core node is running.**
```
git clone https://github.com/joetor5/bitcoin-core-exporter.git
cd bitcoin-core-exporter
```

:two: **Create a Python venv and install dependencies**
```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

:three: **Start the exporter**
```
chmod +x bitcoin_exporter.py
./bitcoin_exporter.py &
```

This will start the exporter http server on port 8000 and collect metrics every 60 seconds. You can select a different port with the -p arg. Run with -h arg for general usage and options.

:four: **View all the metrics (starting with bitcoin_)**
```
curl http://localhost:8000/metrics

```
:five: **Modify the prometheus.yml config for pulling these metrics from the exporter**
```
scrape_configs:

  - job_name: "bitcoin-core"
    scrape_interval: 60s
    static_configs:
      - targets: ["localhost:8000"]

```

:six: **Stop the exporter**
```
pkill -f bitcoin_exporter
```


### Make Setup

:gear:

:one: **Install `make` (if not already installed)**
```sh
# Linux (Ubuntu)
sudo apt install make 

# macOS
brew install make      
```

:two: **Set up the virtual environment**
```sh
make venv
```

:three: **Start the exporter**
```sh
make run
```

:four: **Stop the exporter**

```sh
make stop
```

:five: **Reset the virtual environment (optional)**

If you want to reset your environment, you can delete the virtual environment and set it up again:
```sh
make clean  # Removes the virtual environment
make venv   # Recreates the virtual environment
```

:six: **Enable auto-start on reboot (optional)**

If you want the Bitcoin Core exporter to start automatically when your system reboots, you can run:

```sh
make boot
```

This will:
* Generate a startup script (~/.bitcoin_exporter_boot.sh)
* Register the script in crontab to run on reboot

You can verify the scheduled job with:
```sh
crontab -l
```

If you want to remove the auto-start feature, run:
```sh
crontab -e
```

and delete the line that contains: `@reboot ~/.bitcoin_exporter_boot.sh`


### Docker Setup

:whale:

:one: **Install Docker (if not already installed)**
```sh
# Linux (Ubuntu)
sudo apt update
sudo apt install docker.io -y
sudo systemctl start docker
sudo systemctl enable docker
```

To check if Docker is installed:
```sh
docker --version
sudo systemctl status docker
```
:white_check_mark: If you see the Docker version and the service active (running), installation is complete.

:two: **Add user to Docker group (optional, prevents needing `sudo`)**
```sh
sudo usermod -aG docker $USER
newgrp docker
```

:three: **Start the container (Docker Compose)**

In the project root directory, run:
```sh
docker compose up -d
```
:white_check_mark: This will build the Docker image, start running it in the background, and set it to start on system boot.

If for some reason you can't run the Docker compose command, execute step #4 and #5 to build and run the image manually.

:four: **Build the Docker image (skip if step #3 was executed)**

In the project root directory, run:
```sh
docker build -t bitcoin-exporter .
```
:white_check_mark: This will create a Docker image named bitcoin-exporter.

:five: **Run the container (skip if step #3 was executed)**

To start the exporter in a container:
```sh
docker run -d -p 8000:8000 --name bitcoin-exporter bitcoin-exporter
```
:white_check_mark: This runs bitcoin_exporter.py in the background.

:six: **Verify that it's running**

Check running containers:
```sh
docker ps
```
If the bitcoin-exporter container is running, test the metrics endpoint:
```sh
curl http://localhost:8000/metrics
```
:white_check_mark: If you see Bitcoin metrics, the exporter is working!

:seven: **Stop and remove the container (Docker Compose)**

```sh
docker compose down
```

:eight: **Stop and remove the container (manual, skip if step #7 was executed)**

To stop the running container:
```sh
docker stop bitcoin-exporter
```
To remove the container:
```sh
docker rm bitcoin-exporter
```
To delete the image:
```sh
docker rmi bitcoin-exporter
```
