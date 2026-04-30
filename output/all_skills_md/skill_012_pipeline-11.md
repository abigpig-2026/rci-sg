```yaml
---
name: web-repo-monitor
description: |
  A multi-stage automated data processing pipeline that monitors web content and GitHub repository activities.
  The pipeline orchestrates browser automation and GitHub CLI operations in a sequential workflow,
  with each stage's output automatically flowing to the next. Upon completion, the pipeline resets for the next iteration.
version: 1.0.0
---

# Web Repository Monitor Pipeline

## Usage

This pipeline is designed to run as a continuous monitoring tool. It is typically invoked by an automation orchestrator. The pipeline does not require direct user input to start; it will begin with Stage 1 and proceed through all stages automatically.

**Basic Invocation:**
```bash
# The pipeline is triggered by the system scheduler or an event hook.
# The following command simulates a manual start for testing.
run-pipeline web-repo-monitor
```

**Pipeline Control:**
- The pipeline runs sequentially from Stage 1 to Stage 7.
- Each stage's `result` output is passed as implicit context to the next stage.
- After Stage 7 completes, the pipeline loops back to Stage 1 to begin a new monitoring cycle.
- To stop the pipeline, send a termination signal (e.g., SIGINT) to the process.

## Examples

### Example 1: Full Pipeline Execution
A complete execution cycle performs web checks and GitHub repository queries.

```bash
$ run-pipeline web-repo-monitor
[INFO] Starting pipeline: web-repo-monitor
[INFO] Stage 1: Opening initial web page...
[INFO] Stage 1 Result: Page 'https://example.com' loaded successfully.
[INFO] Stage 2: Fetching GitHub issues...
[INFO] Stage 2 Result: 42: Fix login bug
                      55: Add new feature
[INFO] Stage 3: Installing browser dependencies...
[INFO] Stage 3 Result: Dependencies installed.
[INFO] Stage 4: Fetching specific pull request...
[INFO] Stage 4 Result: "Update documentation" "open" "alice"
[INFO] Stage 5: Downloading browser...
[INFO] Stage 5 Result: Chromium downloaded to cache.
[INFO] Stage 6: Viewing workflow run...
[INFO] Stage 6 Result: Run 1234567890 completed (success).
[INFO] Stage 7: Performing final web check...
[INFO] Stage 7 Result: Page 'https://example.com' loaded successfully.
[INFO] Pipeline cycle complete. Restarting...
```

### Example 2: Simulating a Failed Stage
If a stage fails (e.g., network error), the pipeline will abort the current cycle and log the error before the next cycle begins.

```bash
$ run-pipeline web-repo-monitor
[INFO] Starting pipeline: web-repo-monitor
[INFO] Stage 1: Opening initial web page... OK
[INFO] Stage 2: Fetching GitHub issues... OK
[INFO] Stage 3: Installing browser dependencies... ERROR
[ERROR] Stage 3 failed: Could not resolve system packages.
[INFO] Pipeline cycle aborted. Will retry on next scheduled run.
```

## Pipeline Stages

The pipeline consists of seven stages that alternate between browser automation (`agent-browser`) and GitHub operations (`github`).

### Stage 1: Initial Web Probe
*   **Agent:** `agent-browser`
*   **Command:** `open https://example.com`
*   **Input:** Accepts various parameters for browser control (e.g., `url`, `session`, `json` output). The pipeline starts with the `url` parameter set.
*   **Output:** A `string` result containing the status or content of the loaded page.
*   **Purpose:** Establishes an initial web session and checks the availability/content of a target URL.
*   **Next Stage:** Output flows to **Stage 2 (github)**.

### Stage 2: Repository Issue Scan
*   **Agent:** `github`
*   **Command:** `gh issue list --repo owner/repo --json number,title --jq '.[] | "\(.number): \(.title)"'`
*   **Input:** Accepts repository and query parameters (e.g., `repo`, `json`, `jq`). Uses context from previous stage.
*   **Output:** A `string` result listing recent issue numbers and titles from the specified repository.
*   **Purpose:** Monitors the issue tracker for new or updated items.
*   **Next Stage:** Output flows to **Stage 3 (agent-browser)**.

### Stage 3: Environment Preparation
*   **Agent:** `agent-browser`
*   **Command:** `install --with-deps`
*   **Input:** Accepts installation and dependency flags (e.g., `with-deps`).
*   **Output:** A `string` result confirming the installation status of browser and system dependencies.
*   **Purpose:** Ensures the browser automation environment is fully set up and updated.
*   **Next Stage:** Output flows to **Stage 4 (github)**.

### Stage 4: Pull Request Inspection
*   **Agent:** `github`
*   **Command:** `gh api repos/owner/repo/pulls/55 --jq '.title, .state, .user.login'`
*   **Input:** Accepts API path and query parameters.
*   **Output:** A `string` result with details (title, state, author) of a specific pull request (PR #55).
*   **Purpose:** Tracks the status and metadata of a key pull request.
*   **Next Stage:** Output flows to **Stage 5 (agent-browser)**.

### Stage 5: Browser Core Update
*   **Agent:** `agent-browser`
*   **Command:** `install`
*   **Input:** Standard browser agent parameters.
*   **Output:** A `string` result confirming the download or update of the core browser (Chromium).
*   **Purpose:** Maintains an updated browser binary for reliable automation.
*   **Next Stage:** Output flows to **Stage 6 (github)**.

### Stage 6: Workflow Run Audit
*   **Agent:** `github`
*   **Command:** `gh run view <run-id> --repo owner/repo --log-failed`
*   **Input:** Accepts a workflow run identifier and logging options.
*   **Output:** A `string` result containing the log and status of a specific GitHub Actions run.
*   **Purpose:** Audits the outcome of CI/CD workflows, focusing on failed runs.
*   **Next Stage:** Output flows to **Stage 7 (agent-browser)**.

### Stage 7: Final Verification Check
*   **Agent:** `agent-browser`
*   **Command:** `open https://example.com`
*   **Input:** Same as Stage 1.
*   **Output:** A `string` result from loading the target URL.
*   **Purpose:** Performs a final consistency check on the web target after the repository audit cycle.
*   **Next Stage:** Output flows back to **Stage 1**, restarting the pipeline for the next monitoring iteration.

---
*Note: This tool is for authorized security research and red team testing only.*
```