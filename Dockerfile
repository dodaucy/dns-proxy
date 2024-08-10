# syntax=docker/dockerfile:1

FROM debian:bullseye-slim

# Install python3
RUN apt-get update
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y python3 python3-pip
RUN apt-get clean
RUN rm -rf /var/lib/apt/lists/*

# Create app directory
RUN mkdir /app
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt
RUN rm requirements.txt

# Copy files
COPY . .

# Python support
ENV PYTHONUNBUFFERED=true

# Start app
CMD ["python3", "main.py"]
