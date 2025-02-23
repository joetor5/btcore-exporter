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
chmod +x bitcoin_exporter.py
./bitcoin_exporter.py &
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

### ⚙️ Makefile Setup
If the repository contains a `Makefile`, you can use it to simplify setup and management.

### **1️⃣ Install `make` (if not already installed)**
   ```sh
   # Ubuntu (WSL)
   sudo apt install make 

   # macOS
   brew install make      

   # Windows (PowerShell, Chocolatey required)
   choco install make     

# make stop (Not available in the current Makefile)

Note for Windows users:
・Makefile does not work in Windows PowerShell natively.
・It is recommended to use WSL (Windows Subsystem for Linux) to avoid issues.

2️⃣ Set up the virtual environment
   make venv

3️⃣ Start the exporter
   make run

4️⃣ Stop the exporter
This Makefile does not have a make stop command, but you can stop the process manually:
   pkill -f bitcoin_exporter.py  # Linux/macOS

On Windows (PowerShell), use:
   taskkill /IM python.exe /F

5️⃣ Reset the virtual environment (optional)
If you want to reset your environment, you can delete the virtual environment and set it up again:
```sh
   make clean  # Removes the virtual environment
   make venv   # Recreates the virtual environment

6️⃣ Enable auto-start on reboot (optional)
If you want the Bitcoin Core exporter to start automatically when your system reboots, you can run:

```sh
   make boot

This will:
・Generate a startup script (~/.bitcoin_exporter_boot.sh)
・Register the script in crontab to run on reboot

You can verify the scheduled job with:
   crontab -l

If you want to remove the auto-start feature, run:
   crontab -e

and delete the line that contains:
   @reboot ~/.bitcoin_exporter_boot.sh


### 🐳 Docker Setup
You can run `bitcoin_exporter.py` in a Docker container for easier deployment.

---

1️⃣ Install Docker (if not already installed)
```sh
# Ubuntu (WSL)
   sudo apt update
   sudo apt install docker.io -y
   sudo systemctl start docker
   sudo systemctl enable docker

# Add user to Docker group (optional, prevents needing `sudo`)
   sudo usermod -aG docker $USER
   newgrp docker

To check if Docker is installed:
   docker --version

#✅ If you see the Docker version, installation is complete.#

2️⃣ Build the Docker image
In the project root directory, run:
   docker build -t bitcoin-exporter .
✅ This will create a Docker image named bitcoin-exporter.

3️⃣ Run the container
To start the exporter in a container:
   docker run -d -p 8000:8000 --name bitcoin-exporter bitcoin-exporter
✅ This runs bitcoin_exporter.py in the background.

4️⃣ Verify that it's running
Check running containers:
   docker ps
If the bitcoin-exporter container is running, test the metrics endpoint:
   curl http://localhost:8000/metrics
✅ If you see Bitcoin metrics, the exporter is working!

5️⃣ Stop and remove the container
To stop the running container:
   docker stop bitcoin-exporter
To remove the container:
   docker rm bitcoin-exporter
To delete the image:
   docker rmi bitcoin-exporter