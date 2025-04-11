import os
import requests

# Retrieve configuration from environment variables.
gravitee_url = os.getenv("GRAVITEE_URL")
admin_token = os.getenv("ADMIN_TOKEN")

if not gravitee_url or not admin_token:
    print("Error: GRAVITEE_URL and ADMIN_TOKEN must be set.")
    exit(1)

# Remove any trailing slash from the base URL.
BASE_URL = gravitee_url.rstrip("/")

# Headers for authentication.
headers = {
    "Authorization": f"Bearer {admin_token}",
    "Content-Type": "application/json"
}

# List of application IDs to delete.
app_ids = [
    "0bb96fe8-f419-44ee-b96f-e8f41954eee9",
]


 

def delete_app(app_id):
    """Delete an application by its ID."""
    url = f"{BASE_URL}/applications/{app_id}"
    print(f"Deleting application {app_id} at {url}")
    response = requests.delete(url, headers=headers)
    if response.status_code == 204:
        print(f"Application {app_id} deleted successfully.")
    else:
        print(f"Failed to delete application {app_id}: {response.status_code} - {response.text}")

def main():
    for app_id in app_ids:
        delete_app(app_id)

if __name__ == "__main__":
    main()
