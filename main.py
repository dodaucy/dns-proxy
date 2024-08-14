import socket
import select
from typing import Union

import yaml


BUFFER_SIZE = 512
HEADER_SIZE = 12
CLIENT_TIMEOUT = 5
SERVER_TIMEOUT = 15

allowed_address: Union[str, None] = None


with open("data/config.yaml", "r") as file:
    config = yaml.safe_load(file)


def forward_request(data: bytes) -> bytes:
    # Create a UDP socket to communicate with the real DNS server
    dns_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    dns_socket.settimeout(SERVER_TIMEOUT)
    dns_socket.sendto(data, (config["dns_server"]["address"], config["dns_server"]["port"]))

    # Receive the DNS response from the real DNS server
    response = None
    try:
        response, _ = dns_socket.recvfrom(BUFFER_SIZE)
    except socket.timeout:
        print("Forwarding request timeout")
        pass
    dns_socket.close()
    return response


def is_blocked(client_address, domain: str) -> bool:
    global allowed_address

    # Check if the request wants to resolve the auth domain
    if domain == config["auth_domain"]:
        print("Updating allowed address")
        allowed_address = client_address[0]
        return True

    # Check if the request is from the allowed address
    if allowed_address != client_address[0]:
        print("Address not allowed")
        return True

    # Check if the domain is in the blocked list
    for blocked_domain in config["blocked_domains"]:
        if blocked_domain == domain or (
            blocked_domain.startswith("*.")
            and domain.endswith(blocked_domain[2:])
        ):
            print("Domain blocked")
            return True

    return False


def extract_domain_name(data: bytes) -> str:
    # Skip the header
    offset = HEADER_SIZE

    domain_name = []

    # Read domain name from the query section
    while True:
        length = data[offset]
        if length == 0:
            break
        offset += 1
        domain_name.append(data[offset: offset + length].decode("utf-8"))
        offset += length

    return ".".join(domain_name)


def generate_block_response(data: bytes) -> bytes:
    # Construct a DNS response indicating the query is blocked
    transaction_id = data[:2]
    flags = b"\x81\x83"  # Standard query response, refused
    qdcount = b"\x00\x01"  # One question
    ancount = b"\x00\x00"  # Zero answers
    nscount = b"\x00\x00"  # Zero authority records
    arcount = b"\x00\x00"  # Zero additional records

    # Return the header and the original query
    return transaction_id + flags + qdcount + ancount + nscount + arcount + data[12:]


def main():
    # Create a UDP socket to listen for incoming DNS requests
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.settimeout(CLIENT_TIMEOUT)
    server_socket.bind((config["listen"]["address"], config["listen"]["port"]))
    print(f"DNS Proxy listening on {config['listen']['address']}:{config['listen']['port']}")

    while True:
        # Receive DNS request from client
        try:
            data, client_address = server_socket.recvfrom(BUFFER_SIZE)
        except socket.timeout:
            print("Timeout")
            continue
        print(f"<<< Received request from {client_address}")

        # Check if the request is too small
        if len(data) <= HEADER_SIZE:
            print("Request too small")
            continue

        domain = extract_domain_name(data)
        print(f"Queried domain: {domain}")

        # Check if the request should be blocked
        if is_blocked(client_address, domain):
            print("Blocking request")
            response = generate_block_response(data)
        else:
            # Forward the DNS request to the real DNS server
            print("Forwarding request")
            response = forward_request(data)

        # Send the DNS response back to the client
        server_socket.sendto(response, client_address)
        print(f">>> Sent response to {client_address}")


main()
