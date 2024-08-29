# syntax=docker/dockerfile:1

FROM debian:bookworm-slim

# Install python3
RUN apt-get update
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y python3 python3-pip python3-venv
RUN apt-get clean
RUN rm -rf /var/lib/apt/lists/*

# Create app directory
RUN mkdir /app
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN python3 -m venv venv
RUN venv/bin/pip install --no-cache-dir -r requirements.txt
RUN rm requirements.txt

# Copy files
COPY . .

# Python support
ENV PYTHONUNBUFFERED=true

# Start app
CMD ["venv/bin/python", "main.py"]
