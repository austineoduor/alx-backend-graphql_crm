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

def update_low_stock():
    graphql_url = "http://localhost:8000/graphql"
    mutation = """
    mutation {
        updateLowStockProducts {
            updatedProducts {
                name
                stock
            }
            message
        }
    }
    """

    try:
        response = requests.post(
            graphql_url,
            json={"query": mutation},
            headers={"Content-Type": "application/json"},
            timeout=10
        )

        log_path = "/tmp/low_stock_updates_log.txt"
        timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")

        if response.status_code == 200:
            data = response.json()
            updated = data.get("data", {}).get("updateLowStockProducts", {}).get("updatedProducts", [])
            message = data.get("data", {}).get("updateLowStockProducts", {}).get("message", "No message")

            with open(log_path, "a") as f:
                f.write(f"{timestamp} {message}\n")
                for p in updated:
                    f.write(f"    - {p['name']}: {p['stock']}\n")
        else:
            with open(log_path, "a") as f:
                f.write(f"{timestamp} ERROR: {response.status_code} {response.text}\n")

    except Exception as e:
        with open("/tmp/low_stock_updates_log.txt", "a") as f:
            f.write(f"{timestamp} EXCEPTION: {str(e)}\n")