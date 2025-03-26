import requests
import logging
import time
from requests.adapters import HTTPAdapter, Retry
from concurrent.futures import ThreadPoolExecutor

# Configure logging
logging.basicConfig(filename='app_creation.log', level=logging.INFO)

# Configure these variables
gravitee_url = "https://your-gravitee-instance/api"
admin_token = "YOUR_ADMIN_TOKEN"
api_name = "edu-echo"

headers = {
    "Authorization": f"Bearer {admin_token}",
    "Content-Type": "application/json"
}

session = requests.Session()
retries = Retry(total=5, backoff_factor=0.5, status_forcelist=[429, 500, 502, 503, 504])
session.mount('https://', HTTPAdapter(max_retries=retries))
session.headers.update(headers)

def create_application(app_name):
    data = {"name": app_name, "description": f"Automated app {app_name}", "type": "SIMPLE"}
    response = session.post(f"{gravitee_url}/applications", json=data)
    response.raise_for_status()
    return response.json()

def get_api_id(api_name):
    response = session.get(f"{gravitee_url}/apis")
    response.raise_for_status()
    apis = response.json()
    for api in apis:
        if api["name"] == api_name:
            return api["id"]
    raise Exception(f"API named '{api_name}' not found.")

def create_subscription(api_id, application_id):
    data = {"application": application_id, "plan": get_api_plan_id(api_id)}
    response = session.post(f"{gravitee_url}/apis/{api_id}/subscriptions", json=data)
    response.raise_for_status()
    return response.json()

def get_api_plan_id(api_id):
    response = session.get(f"{gravitee_url}/apis/{api_id}/plans")
    response.raise_for_status()
    plans = response.json()
    if plans:
        return plans[0]["id"]
    raise Exception(f"No plans available for API {api_id}")

def get_request(api_id):
    response = session.get(f"{gravitee_url}/apis/{api_id}")
    response.raise_for_status()
    return response.json()

def process_application(i, api_id):
    try:
        app_name = f"AutomatedApp-{i}"
        logging.info(f"Creating application: {app_name}")
        application = create_application(app_name)

        logging.info(f"Creating subscription for application ID: {application['id']}")
        subscription = create_subscription(api_id, application["id"])

        api_info = get_request(api_id)
        logging.info(f"Completed application {app_name}")

        if i % 2 == 0:
            logging.info(f"Progress: {i} applications processed.")

        time.sleep(0.05)

    except Exception as e:
        logging.error(f"Error at application {i}: {e}")

# Main script execution
api_id = get_api_id(api_name)

with ThreadPoolExecutor(max_workers=4) as executor:
    executor.map(lambda i: process_application(i, api_id), range(1, 9))
