import requests
import logging
import time
import os
from requests.adapters import HTTPAdapter, Retry
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
from logging.handlers import RotatingFileHandler

# Configure rotating log handler
log_handler = RotatingFileHandler('app_creation.log', maxBytes=1000000, backupCount=5)
logging.basicConfig(handlers=[log_handler], level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Retrieve configuration from environment variables
gravitee_url = os.getenv("GRAVITEE_URL")
admin_token = os.getenv("ADMIN_TOKEN")

headers = {
    "Authorization": f"Bearer {admin_token}",
    "Content-Type": "application/json"
}

session = requests.Session()
retries = Retry(total=15, backoff_factor=0.5, status_forcelist=[429, 500, 502, 503, 504])
session.mount('https://', HTTPAdapter(max_retries=retries))
session.headers.update(headers)

def create_application(app_name):
    data = {"name": app_name, "description": f"Automated app {app_name}", "type": "SIMPLE"}
    response = session.post(f"{gravitee_url}/applications", json=data)
    response.raise_for_status()
    return response.json()

def get_existing_plan_id(api_id, plan_name):
    url = f"http://localhost:8083/management/v1/organizations/DEFAULT/environments/DEFAULT/apis/{api_id}/plans"
    response = session.get(url)
    response.raise_for_status()
    plans = response.json()  # This returns a list in v1
    for plan in plans:
        if isinstance(plan, dict) and plan.get("name") == plan_name:
            return plan["id"]
    raise Exception(f"Plan named '{plan_name}' not found for API {api_id}.")


def create_subscription_v2(api_id, application_id, plan_id):
    url = f"http://localhost:8083/management/v1/organizations/DEFAULT/environments/DEFAULT/apis/{api_id}/subscriptions"

    headers_override = {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json"
    }

    data = {
        "application": application_id,   # ✅ Correct field name
        "plan": plan_id,                 # ✅ Correct field name
        "request": f"Automated subscription for app {application_id}"
    }

    response = requests.post(url, headers=headers_override, json=data)

    if response.status_code >= 400:
        print(f"❌ Subscription failed: {response.status_code}")
        print(response.text)

    response.raise_for_status()
    return response.json()



def get_subscription_api_key(api_id, subscription_id):
    url = f"http://localhost:8083/management/organizations/DEFAULT/environments/DEFAULT/apis/{api_id}/subscriptions/{subscription_id}/apikeys"
    response = session.get(url)
    response.raise_for_status()
    api_keys = response.json()
    if api_keys and isinstance(api_keys, list):
        return api_keys[0]['key']
    raise Exception(f"No API key found for subscription {subscription_id}")

def perform_request_with_apikey(api_key, index):
    api_endpoint = "http://localhost:8082/echov2"
    headers = {
        "Content-Type": "application/json",
        "X-Gravitee-Api-Key": api_key
    }
    print(f"🔐 Using API key: {api_key}")

    for attempt in range(20):
        try:
            response = requests.get(api_endpoint, headers=headers)
            response.raise_for_status()
            print(f"✅ Test Call{index} successful")
            return response
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401 and attempt < 19:
                print(f"⚠️ Test Call{index} failed with 401, retrying ({attempt+1}/20)...")
                time.sleep(0.5)
            else:
                raise

def process_application(i, api_id, plan_id, progress_bar):
    try:
        app_name = f"AutomatedApp-{i}"
        application = create_application(app_name)
        print(f"✅ App{i} created successfully")

        subscription = create_subscription_v2(api_id, application["id"], plan_id)
        print(f"✅ Subscription{i} created successfully")

        time.sleep(1)  # Increased wait to 1s

        api_key = get_subscription_api_key(api_id, subscription['id'])
        perform_request_with_apikey(api_key, i)

    except Exception as e:
        print(f"❌ Error at application {i}: {e}")
        logging.error(f"Application {i} failed: {e}")
    finally:
        progress_bar.update(1)

# Main script execution
if __name__ == "__main__":
    api_id = "88e1120c-6feb-4f4c-a112-0c6febff4c97"
    plan_name = "edu_nat"
    plan_id = get_existing_plan_id(api_id, plan_name)

    start_from = 1
    total_apps_to_create = 2

    with tqdm(total=total_apps_to_create, desc="Progress", unit="app") as progress_bar:
        with ThreadPoolExecutor(max_workers=8) as executor:
            for i in range(start_from, start_from + total_apps_to_create):
                executor.submit(process_application, i, api_id, plan_id, progress_bar)
