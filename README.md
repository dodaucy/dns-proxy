# DNS Proxy

Simple python DNS proxy with auth and blocklist.

![showcase](./showcase.png)

## Docker

```bash
git clone https://github.com/dodaucy/dns-proxy.git
cd dns-proxy

docker build -t dns-proxy .

docker run -d \  # Run in background
  -p $(hostname -I | awk '{print $1}'):53:5353/udp \
  -v ./data:/app/data \
  --name dns-proxy \
  --restart always \
  dns-proxy

nano data/config.yaml  # Edit config

docker logs -f dns-proxy  # Log
```

## Without docker

```bash
git clone https://github.com/dodaucy/dns-proxy.git
cd dns-proxy

python3 -m pip install -Ur requirements.txt

mkdir data
cp example_config.yaml data/config.yaml
nano data/config.yaml  # Edit config

python3 main.py  # Run
```
