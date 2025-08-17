from celery import shared_task
from datetime import datetime
import requests

@shared_task
def generate_crm_report():
    # GraphQL query to fetch customer and order data
    graphql_url = "http://localhost:8000/graphql"
    query = """
    query {
        totalCustomers: allCustomers {
            count
        }
        totalOrders: allOrders {
            count
        }
        totalRevenue: allOrders {
            totalAmount
        }
    }
    """
    
    try:
        response = requests.post(
            graphql_url,
            json={"query": query},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            total_customers = data.get("data", {}).get("totalCustomers", {}).get("count", 0)
            total_orders = data.get("data", {}).get("totalOrders", {}).get("count", 0)
            total_revenue = sum(order['totalAmount'] for order in data.get("data", {}).get("totalRevenue", []))
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            report_message = f"{timestamp} - Report: {total_customers} customers, {total_orders} orders, ${total_revenue} revenue"
            
            log_path = "/tmp/crm_report_log.txt"
            with open(log_path, "a") as f:
                f.write(report_message + "\n")
        else:
            raise Exception(f"GraphQL query failed with status {response.status_code}")
        
    except Exception as e:
        # Log error if anything goes wrong
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        error_message = f"{timestamp} - ERROR: {str(e)}"
        with open("/tmp/crm_report_log.txt", "a") as f:
            f.write(error_message + "\n")