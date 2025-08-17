from datetime import datetime
from gql.transport.requests import RequestsHTTPTransport
from gql import gql, Client
import requests

def log_crm_heartbeat():
    timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    message = f"{timestamp} CRM is alive"

    log_path = "/tmp/crm_heartbeat_log.txt"
    with open(log_path, "a") as f:
        f.write(message + "\n")

    # Optional: check GraphQL hello field
    try:
        response = requests.post(
            "http://localhost:8000/graphql",
            json={"query": "{ hello }"},
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        if response.status_code == 200:
            print("GraphQL heartbeat OK:", response.json())
        else:
            print("GraphQL error:", response.status_code)
    except Exception as e:
        print("GraphQL check failed:", e)