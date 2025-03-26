import os
import requests

# Retrieve configuration from environment variables.
gravitee_url = os.getenv("GRAVITEE_URL")
admin_token = os.getenv("ADMIN_TOKEN")

if not gravitee_url or not admin_token:
    print("Error: GRAVITEE_URL and/or ADMIN_TOKEN environment variables are not set.")
    exit(1)

# Since GRAVITEE_URL already contains the management path, organizations, and environments,
# we simply remove any trailing slash.
BASE_URL = gravitee_url.rstrip("/")

# Headers for authentication.
headers = {
    "Authorization": f"Bearer {admin_token}",
    "Content-Type": "application/json"
}

def get_all_applications():
    """
    Retrieve all applications from the Gravitee Management API.
    """
    url = f"{BASE_URL}/applications"
    print(f"Fetching applications from: {url}")
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching applications: Status {response.status_code} - {response.text}")
        return []

def delete_application(app_id, app_name):
    """
    Deletes an application by its ID.
    """
    url = f"{BASE_URL}/applications/{app_id}"
    print(f"Deleting {app_name} (ID: {app_id}) at: {url}")
    response = requests.delete(url, headers=headers)
    if response.status_code == 204:
        print(f"Deleted {app_name} successfully.")
    else:
        print(f"Error deleting {app_name}: {response.status_code} - {response.text}")

def main():
    # Create a set of target application names AutomatedApp-1 to AutomatedApp-10.
    target_names = {f"AutomatedApp-{i}" for i in range(1, 11)}
    
    # Fetch all applications.
    apps = get_all_applications()
    if not apps:
        print("No applications found or an error occurred.")
        return

    # Loop through applications and delete those matching the target names.
    for app in apps:
        name = app.get("name")
        if name in target_names:
            app_id = app.get("id")
            delete_application(app_id, name)
        else:
            print(f"Skipping {name}.")

if __name__ == "__main__":
    main()
