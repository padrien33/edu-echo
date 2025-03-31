## 📘 Gravitee Application & Subscription Automation

This script automates the creation of applications, subscriptions, and API key-based test calls in **Gravitee APIM v4** using the Gravitee Management API.

---

### 🚀 Features

- ✅ Automatically creates applications (`SIMPLE` type)
- ✅ Subscribes each app to a predefined plan (e.g. `edu_nat`)
- ✅ Fetches the generated API key for each subscription
- ✅ Performs a test call to a running Gravitee gateway (e.g. `/echo`)
- ✅ Retries test calls if they return unauthorized (401)
- ✅ Logs errors to `app_creation.log` with rotation
- ✅ Displays a progress bar using `tqdm`
- ✅ Supports parallel execution for faster processing

---

### ⚙️ Requirements

- Python 3.8+
- Python packages:
  ```bash
  pip install requests tqdm
  ```

- Running Gravitee APIM stack (Gateway, Management API)
- Ensure the following environment variables are set:
  ```bash
  export GRAVITEE_URL=http://localhost:8083/management/v2/organizations/DEFAULT/environments/DEFAULT
  export ADMIN_TOKEN=<your_admin_token>
  ```

---

### 📄 Usage

1. **Edit the script if needed**, e.g.:
   - `total_apps_to_create = 100`
   - `plan_name = "edu_nat"`
   - `api_id = "<your_api_id>"`

2. **Run the script**:
   ```bash
   python load.py
   ```

3. **Monitor progress**:
   - CLI will show a progress bar and status logs
   - Logs are saved in `app_creation.log`

---

### ⚙️ Customization Tips

- **Parallelism**: Adjust the number of threads with `ThreadPoolExecutor(max_workers=X)`
- **Sync Delay**: For better performance, ensure Gravitee Gateway syncs quickly. You can override it in Docker Compose:
  ```yaml
  environment:
    - gravitee_services_sync_delay=500
    - gravitee_services_sync_unit=MILLISECONDS
  ```

