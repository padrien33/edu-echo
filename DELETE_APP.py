import os
import requests

# Config
gravitee_url = os.getenv("GRAVITEE_URL")
gravitee_api_url = os.getenv("GRAVITEE_API_URL", "http://localhost:8083/management/v2/organizations/DEFAULT/environments/DEFAULT")
admin_token = os.getenv("ADMIN_TOKEN")

if not gravitee_url or not admin_token:
    print("❌ GRAVITEE_URL or ADMIN_TOKEN not set.")
    exit(1)

BASE_URL = gravitee_url.rstrip("/")
API_BASE_URL = gravitee_api_url.rstrip("/")
API_ID = "fe743d3b-0ae1-40c7-b43d-3b0ae1b0c716"

headers = {
    "Authorization": f"Bearer {admin_token}",
    "Content-Type": "application/json"
}

# --- APPLICATIONS ---
def get_all_applications():
    url = f"{BASE_URL}/applications"
    print(f"📥 Fetching applications: {url}")
    response = requests.get(url, headers=headers)
    return response.json() if response.status_code == 200 else []

def delete_application(app_id, name):
    url = f"{BASE_URL}/applications/{app_id}"
    print(f"🗑️ Deleting application {name} (ID: {app_id})")
    res = requests.delete(url, headers=headers)
    if res.status_code == 204:
        print(f"✅ Deleted application {name}")
    else:
        print(f"❌ Failed to delete application {name}: {res.status_code} - {res.text}")

# --- PLANS ---
def get_plans_for_api(api_id):
    url = f"{API_BASE_URL}/apis/{api_id}/plans"
    print(f"📥 Fetching plans: {url}")
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        data = res.json()
        return data.get("data", data)
    else:
        print(f"❌ Failed to fetch plans: {res.status_code} - {res.text}")
        return []

def delete_plan(api_id, plan_id, name):
    url = f"{API_BASE_URL}/apis/{api_id}/plans/{plan_id}"
    print(f"🗑️ Deleting plan {name} (ID: {plan_id})")
    res = requests.delete(url, headers=headers)
    if res.status_code == 204:
        print(f"✅ Deleted plan {name}")
    else:
        print(f"❌ Failed to delete plan {name}: {res.status_code} - {res.text}")

# --- SUBSCRIPTIONS ---
def get_all_subscriptions():
    url = f"{BASE_URL}/subscriptions"
    print(f"📥 Fetching subscriptions: {url}")
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        data = res.json()
        return data.get("data", data)
    else:
        print(f"❌ Failed to fetch subscriptions: {res.status_code} - {res.text}")
        return []

def delete_subscription(app_id, sub_id):
    url = f"{BASE_URL}/applications/{app_id}/subscriptions/{sub_id}"
    print(f"🗑️ Deleting subscription {sub_id} (app: {app_id})")
    res = requests.delete(url, headers=headers)
    if res.status_code == 204:
        print(f"✅ Deleted subscription {sub_id}")
    else:
        print(f"❌ Failed to delete subscription {sub_id}: {res.status_code} - {res.text}")

# --- MAIN ---
def main():
    target_app_names = {f"AutomatedApp-{i}" for i in range(1, 101)}
    target_plan_names = {f"Plan-App-{i}" for i in range(1, 101)}

    # 1. Delete Applications
    apps = get_all_applications()
    for app in apps:
        name = app.get("name")
        if name in target_app_names:
            delete_application(app.get("id"), name)
        else:
            print(f"⏭️ Skipping application {name}")

    # 2. Delete Plans and collect plan IDs
    plans = get_plans_for_api(API_ID)
    target_plan_ids = set()
    for plan in plans:
        name = plan.get("name")
        pid = plan.get("id")
        if name in target_plan_names:
            delete_plan(API_ID, pid, name)
            target_plan_ids.add(pid)
        else:
            print(f"⏭️ Skipping plan {name}")

    # 3. Delete Subscriptions for the deleted plan IDs
    if target_plan_ids:
        subs = get_all_subscriptions()
        for sub in subs:
            if sub.get("plan") in target_plan_ids:
                delete_subscription(sub.get("application"), sub.get("id"))
            else:
                print(f"⏭️ Skipping subscription {sub.get('id')} (plan: {sub.get('plan')})")
    else:
        print("⚠️ No target plan IDs collected — skipping subscriptions.")

if __name__ == "__main__":
    main()
