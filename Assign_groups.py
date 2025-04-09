import os
import requests

# === CONFIGURATION ===
gravitee_url = os.getenv("GRAVITEE_URL")  # e.g. http://localhost:8083/management/organizations/DEFAULT/environments/DEFAULT
admin_token = os.getenv("ADMIN_TOKEN")
group_id = "3b8f5901-4d8c-4df9-8f59-014d8c2df9e6"  # <-- Replace with your actual group ID
app_prefix = "AutomatedApp-"  # Only assign apps with this prefix

# === HEADERS ===
headers = {
    "Authorization": f"Bearer {admin_token}",
    "Accept": "application/json",
    "Content-Type": "application/json"
}

# === FUNCTIONS ===

def fetch_applications():
    print("📥 Fetching applications...")
    url = f"{gravitee_url}/applications?page=1&size=40000"
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"❌ Failed to fetch applications: {response.status_code} - {response.text}")
        return {}

    apps = response.json()
    filtered = {app["name"]: app["id"] for app in apps if app["name"].startswith(app_prefix)}
    print(f"🔎 Found {len(filtered)} apps starting with '{app_prefix}'")
    return filtered

def assign_app_to_group(app_id, app_name):
    url = f"{gravitee_url}/configuration/groups/{group_id}/memberships"
    payload = {
        "memberId": app_id,
        "memberType": "APPLICATION",
        "role": "APPLICATION:USER"
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code in (200, 201, 204):
        print(f"✅ Assigned {app_name} to group '{group_id}'")
    else:
        print(f"❌ Failed to assign {app_name} ({app_id}): {response.status_code} - {response.text}")


# === MAIN EXECUTION ===

if not gravitee_url or not admin_token:
    print("❗ GRAVITEE_URL or ADMIN_TOKEN is not set.")
    exit(1)

app_ids = fetch_applications()
if not app_ids:
    print("⚠️ No applications matched. Exiting.")
    exit(0)

print(f"🔗 Assigning applications to group: {group_id}")
for name, app_id in app_ids.items():
    assign_app_to_group(app_id, name)

