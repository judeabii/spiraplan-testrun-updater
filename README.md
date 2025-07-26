# Automated Test Run Status Updater for SpiraPlan via SharePoint Tracker

This project is a utility to automate the process of updating test run statuses in SpiraPlan, based on an execution tracker Excel file hosted on SharePoint. The utility parses the tracker, updates test case statuses (e.g., Passed, Failed, Blocked), and links failed/blocked test steps with relevant incident IDs in Spira.

---

### Features
* Secure SharePoint Access using office365 API and .env credentials
* Excel File Parsing using openpyxl to read test case execution data
* Test Set Mapping to SpiraPlan via REST API
* Automated Test Run Status Updates
* Linking Incidents to Test Run Steps (for failed/blocked tests)
* Modular structure to support reusability and extensibility
---
### Tech Stack
* Python 3.9+
* FastAPI (optional extension)
* SpiraPlan REST API
* Office365 Python SDK
* openpyxl
* dotenv
* requests
---
## How It Works

This tool automates release-level QA updates by syncing Excel-tracked test case statuses and incident links with SpiraPlan.

### 1. Excel File Retrieval
* Authenticates with SharePoint using credentials.
* Downloads the Excel tracker for the target release.
* Extracts key fields from each row:
  * `Test Case ID`
  * `Subfunction`
  * `Execution Status`
  * `Incident ID` (optional)

### 2. Excel Parsing & Filtering
* Skips irrelevant rows (e.g., missing data, unexecuted cases).
* Filters rows that belong to the current release and require updates.

### 3. Test Set & Test Case Mapping
* Fetches all **Test Sets** for the specified **Release ID** using SpiraPlan API.
* Matches each Excel row to the correct **Test Set**.
* Retrieves all **Test Cases** linked to that Test Set.

### 4. Test Run Update Workflow
For each relevant test case:
* Fetches the most recent **test run payload** to get the old state.
* Builds a new test run payload with the **updated status**.
* Posts the new test run to SpiraPlan via API.
* Runs in **batches of 50** to handle API rate limits and improve performance.

### 5. Incident Linking Workflow
If an incident is listed in the tracker:
* Fetches the **incident payload** from SpiraPlan.
* Adds the failing **test step references** to the incident description or metadata.
* Sends a `PUT` request to update the incident and link it to the test case.

---

### ⚠️ Disclaimer
This is a personal refactor of an internal automation tool. No sensitive or proprietary information is included. Use responsibly.
