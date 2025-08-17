import requests
from datetime import datetime, timedelta
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

# Configure the transport
transport = RequestsHTTPTransport(
    url="http://localhost:8000/graphql",
    verify=False,
    retries=3,
)

client = Client(transport=transport, fetch_schema_from_transport=False)

# Calculate date range for last 7 days
today = datetime.now()
week_ago = today - timedelta(days=7)

start_date = week_ago.strftime("%Y-%m-%d")
end_date = today.strftime("%Y-%m-%d")

# Define the GraphQL query
query = gql(
    """
    query getRecentOrders($start: Date!, $end: Date!) {
        allOrders(orderDate_Gte: $start, orderDate_Lte: $end) {
            id
            customer {
                email
            }
        }
    }
    """
)

# Execute query
params = {"start": start_date, "end": end_date}
result = client.execute(query, variable_values=params)

# Logging
timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
log_file = "/tmp/order_reminders_log.txt"

with open(log_file, "a") as f:
    for order in result.get("allOrders", []):
        order_id = order["id"]
        email = order["customer"]["email"]
        f.write(f"{timestamp} Order ID: {order_id}, Email: {email}\n")

print("Order reminders processed!")