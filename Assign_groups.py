import os
import requests

# Load environment variables
gravitee_url = os.getenv("GRAVITEE_URL")  # Should be: http://localhost:8083/management/organizations/DEFAULT/environments/DEFAULT
admin_token = os.getenv("ADMIN_TOKEN")
group_id = "your-group-id"  # <-- Replace with the actual group ID

# App name pattern to filter
APP_PREFIX = "AutomatedApp-"

# Headers
headers = {
    "Authorization": f"Bearer {admin_token}",
    "Accept": "application/json",
    "Content-Type": "application/json"
}

def fetch_applications():
    print("📥 Fetching applications...")
    url = f"{gravitee_url}/applications?page=1&size=40000"
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"❌ Failed to fetch applications: {response.status_code} - {response.text}")
        return {}

    apps = response.json()  # It's a list, not an object
    print(f"✅ Retrieved {len(apps)} total applications")

    filtered = {app["name"]: app["id"] for app in apps if app["name"].startswith(APP_PREFIX)}
    print(f"🔎 Found {len(filtered)} apps matching prefix '{APP_PREFIX}'")
    return filtered

def assign_group(app_ids):
    print(f"🔗 Assigning group '{group_id}' to applications...")
    for name, app_id in app_ids.items():
        url = f"{gravitee_url}/applications/{app_id}/groups"
        response = requests.post(url, headers=headers, json=[group_id])
        if response.status_code in (200, 204):
            print(f"✅ Assigned group to {name}")
        else:
            print(f"❌ Failed to assign group to {name} ({app_id}): {response.status_code} - {response.text}")

# Run the script
if __name__ == "__main__":
    app_ids = fetch_applications()
    if app_ids:
        assign_group(app_ids)
    else:
        print("⚠️ No applications to process.")
