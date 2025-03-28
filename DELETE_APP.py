import os
import requests

# Retrieve configuration from environment variables.
gravitee_url = os.getenv("GRAVITEE_URL")
gravitee_api_url = os.getenv("GRAVITEE_API_URL", "http://localhost:8083/management/v2/organizations/DEFAULT/environments/DEFAULT")
admin_token = os.getenv("ADMIN_TOKEN")

if not gravitee_url or not admin_token:
    print("Error: GRAVITEE_URL and/or ADMIN_TOKEN environment variables are not set.")
    exit(1)

# Remove trailing slashes.
BASE_URL = gravitee_url.rstrip("/")
API_BASE_URL = gravitee_api_url.rstrip("/")

# Hard-coded API ID for which the plans belong.
API_ID = "fe743d3b-0ae1-40c7-b43d-3b0ae1b0c716"

# Headers for authentication.
headers = {
    "Authorization": f"Bearer {admin_token}",
    "Content-Type": "application/json"
}

# ----- APPLICATION FUNCTIONS (v1) -----
def get_all_applications():
    """Retrieve all applications from the v1 endpoint."""
    url = f"{BASE_URL}/applications"
    print(f"Fetching applications from: {url}")
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching applications: Status {response.status_code} - {response.text}")
        return []

def delete_application(app_id, app_name):
    """Delete an application by its ID."""
    url = f"{BASE_URL}/applications/{app_id}"
    print(f"Deleting application {app_name} (ID: {app_id}) at: {url}")
    response = requests.delete(url, headers=headers)
    if response.status_code == 204:
        print(f"Deleted application {app_name} successfully.")
    else:
        print(f"Error deleting application {app_name}: {response.status_code} - {response.text}")

# ----- PLAN FUNCTIONS (v2) -----
def get_plans_for_api(api_id):
    """Retrieve all plans for a specific API using the v2 endpoint."""
    url = f"{API_BASE_URL}/apis/{api_id}/plans"
    print(f"Fetching plans for API {api_id} from: {url}")
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        result = response.json()
        # Extract the list of plans from the 'data' key if present.
        if isinstance(result, dict) and "data" in result:
            return result["data"]
        else:
            return result
    else:
        print(f"Error fetching plans for API {api_id}: Status {response.status_code} - {response.text}")
        return []

def delete_plan(api_id, plan_id, plan_name):
    """Delete a plan by its ID from a given API using the v2 endpoint."""
    url = f"{API_BASE_URL}/apis/{api_id}/plans/{plan_id}"
    print(f"Deleting plan {plan_name} (ID: {plan_id}) from API {api_id} at: {url}")
    response = requests.delete(url, headers=headers)
    if response.status_code == 204:
        print(f"Deleted plan {plan_name} successfully.")
    else:
        print(f"Error deleting plan {plan_name}: {response.status_code} - {response.text}")

# ----- MAIN FUNCTION -----
def main():
    # Define target names.
    target_app_names = {f"AutomatedApp-{i}" for i in range(1, 11)}
    target_plan_names = {f"Plan-App-{i}" for i in range(1, 11)}

    # Delete applications.
    apps = get_all_applications()
    if apps:
        for app in apps:
            name = app.get("name", "")
            if name in target_app_names:
                app_id = app.get("id")
                delete_application(app_id, name)
            else:
                print(f"Skipping application {name}.")
    else:
        print("No applications found or an error occurred fetching applications.")

    # Delete plans for the specified API.
    plans = get_plans_for_api(API_ID)
    if not plans:
        print(f"No plans found for API {API_ID}.")
        return

    for plan in plans:
        plan_name = plan.get("name", "")
        if plan_name in target_plan_names:
            plan_id = plan.get("id")
            delete_plan(API_ID, plan_id, plan_name)
        else:
            print(f"Skipping plan {plan_name}.")

if __name__ == "__main__":
    main()
