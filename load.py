import requests
import logging
import time
import os
from requests.adapters import HTTPAdapter, Retry
from concurrent.futures import ThreadPoolExecutor

# Configure logging
logging.basicConfig(filename='app_creation.log', level=logging.INFO)

# Retrieve configuration from environment variables
gravitee_url = os.getenv("GRAVITEE_URL")
admin_token = os.getenv("ADMIN_TOKEN")

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
    print(f"Application {app_name} created successfully.")
    return response.json()

def create_v4_plan(api_id, app_number):
    plan_name = f"Plan-App-{app_number}"
    payload = {
        "name": plan_name,
        "description": f"Plan for app {app_number}",
        "definitionVersion": "4.0.0",
        "mode": "STANDARD",
        "status": "PUBLISHED",
        "security": "API_KEY",
        "flows": [],
        "tags": []
    }
    url = f"{gravitee_url}/apis/{api_id}/plans"
    response = session.post(url, json=payload)
    print(f"Plan creation response: {response.status_code}, {response.text}")
    response.raise_for_status()
    return response.json()["id"]

def create_subscription_v4(api_id, application_id, plan_id):
    data = {
        "applicationId": application_id,
        "planId": plan_id,
        "request": f"Automated subscription for app {application_id} on plan {plan_id}"
    }
    base_url = "http://localhost:8083/management/v2/organizations/DEFAULT/environments/DEFAULT"
    url = f"{base_url}/apis/{api_id}/subscriptions"

    headers_override = {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json"
    }

    print(f"Creating subscription with payload: {data}")
    response = requests.post(url, headers=headers_override, json=data)
    print(f"Subscription request response status: {response.status_code}, body: {response.text}")
    response.raise_for_status()
    print(f"✅ Subscription created successfully for application ID {application_id}.")
    return response.json()

def get_subscription_api_key(api_id, subscription_id):
    url = f"http://localhost:8083/management/organizations/DEFAULT/environments/DEFAULT/apis/{api_id}/subscriptions/{subscription_id}/apikeys"
    response = session.get(url)
    print(f"API key fetch response: {response.status_code}, {response.text}")
    response.raise_for_status()
    api_keys = response.json()
    if api_keys and isinstance(api_keys, list):
        return api_keys[0]['key']
    raise Exception(f"No API key found for subscription {subscription_id}")

def perform_request_with_apikey(api_key):
    api_endpoint = "http://localhost:8082/echo"  # Replace with your actual gateway endpoint
    headers = {"X-Gravitee-Api-Key": api_key}
    response = session.get(api_endpoint, headers=headers)
    response.raise_for_status()
    return response

def process_application(i, api_id):
    try:
        app_name = f"AutomatedApp-{i}"
        logging.info(f"Creating application: {app_name}")
        application = create_application(app_name)

        logging.info(f"Creating v4 plan for application: {app_name}")
        plan_id = create_v4_plan(api_id, i)

        logging.info(f"App ID: {application['id']}, Plan ID: {plan_id}")
        subscription = create_subscription_v4(api_id, application["id"], plan_id)

        time.sleep(1)  # Wait briefly to ensure API key creation

        api_key = get_subscription_api_key(api_id, subscription['id'])
        logging.info(f"Retrieved API Key: {api_key}")

        api_response = perform_request_with_apikey(api_key)
        logging.info(f"API request response for {app_name}: {api_response.status_code}")
        print(f"Application {app_name} created and API call successful.")

        if i % 10 == 0:
            logging.info(f"Progress: {i} applications processed.")

    except Exception as e:
        logging.error(f"Error at application {i}: {e}")
        print(f"Error at application {i}: {e}")

# Main script execution
if __name__ == "__main__":
    api_id = "fe743d3b-0ae1-40c7-b43d-3b0ae1b0c716"  # Replace this with your actual v4 API ID

    start_from = 1
    total_apps_to_create = 3
    with ThreadPoolExecutor(max_workers=4) as executor:
        executor.map(lambda i: process_application(i, api_id),
                     range(start_from, start_from + total_apps_to_create))
