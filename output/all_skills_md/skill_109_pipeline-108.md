```yaml
---
name: web-repo-sync
description: |
  A multi-stage automated data processing pipeline that synchronizes web content monitoring with GitHub repository operations.
  The pipeline orchestrates browser automation and GitHub CLI commands in a sequential workflow, with data automatically flowing between stages.
  Upon completion of all stages, the pipeline restarts for the next iteration of optimization.
version: 1.0.0
---

# web-repo-sync Pipeline

## Usage

This pipeline is designed to run as a continuous, automated workflow. It is typically invoked by a scheduler or trigger mechanism. The pipeline manages its own state and data flow between stages.

**Basic Invocation:**
```bash
# The pipeline is started as a single unit. Internal stage transitions are automatic.
run-pipeline web-repo-sync
```

**Configuration:**
The pipeline may require pre-configured environment variables or context, such as:
- `GITHUB_TOKEN`: For authenticating GitHub CLI commands.
- Target repository details (e.g., `owner/repo`).
- Target URLs for browser stages.

## Examples

### Example 1: Full Pipeline Execution
A complete run of the `web-repo-sync` pipeline performs the following sequence. The output of each stage becomes part of the pipeline's context for potential use in subsequent stages.

```bash
# Starting the pipeline. The following stages execute automatically in order.
$ run-pipeline web-repo-sync
[INFO] Starting web-repo-sync pipeline iteration 1.
[INFO] Stage 1 (agent-browser): Opening initial URL...
[INFO] Stage 2 (github): Fetching issue list from owner/repo...
[INFO] Stage 3 (agent-browser): Installing browser dependencies...
[INFO] Stage 4 (github): Fetching details for pull request #55...
[INFO] Stage 5 (agent-browser): Downloading browser binaries...
[INFO] Stage 6 (github): Listing recent workflow runs...
[INFO] Stage 7 (agent-browser): Opening final URL...
[INFO] Pipeline iteration complete. Restarting for next cycle.
```

### Example 2: Pipeline Context
The pipeline maintains a data context. For instance, the list of issues fetched in Stage 2 could inform actions in later browser stages in a real-world scenario.
```json
{
  "pipeline": "web-repo-sync",
  "current_stage": 4,
  "data": {
    "stage_1_result": "<HTML content from https://example.com>",
    "stage_2_result": "123: Bug fix for login\n124: Feature request for API",
    "stage_3_result": "System dependencies installed successfully."
  }
}
```

## Pipeline Stages

The `web-repo-sync` pipeline consists of seven sequential stages. Each stage completes its task and passes control and contextual data to the next stage automatically.

### Stage 1: Initial Web Probe
*   **Tool:** `agent-browser`
*   **Command:** `open https://example.com`
*   **Description:** Initiates the pipeline by opening a target webpage. This stage is typically used to fetch initial web content, verify site availability, or establish a browsing session.
*   **Input:** Accepts various parameters for browser control (e.g., `url`, `session`, `json` output).
*   **Output:** `result` (string) - The textual or structured content retrieved from the page.
*   **Next Stage:** Automatically proceeds to Stage 2 (github).

### Stage 2: Repository Issue Scan
*   **Tool:** `github` (GitHub CLI)
*   **Command:** `gh issue list --repo owner/repo --json number,title --jq '.[] | "\(.number): \(.title)"'`
*   **Description:** Fetches a list of recent issues from a specified GitHub repository. The `--jq` filter formats the output for readability.
*   **Input:** Accepts repository target, output format (`json`), and query filters (`jq`, `limit`).
*   **Output:** `result` (string) - A formatted list of issue numbers and titles.
*   **Next Stage:** Automatically proceeds to Stage 3 (agent-browser).

### Stage 3: Browser Environment Setup
*   **Tool:** `agent-browser`
*   **Command:** `install --with-deps`
*   **Description:** Prepares the browser automation environment by installing necessary dependencies. On Linux systems, this includes system-level packages required for browser operation.
*   **Input:** Supports installation flags like `--with-deps`.
*   **Output:** `result` (string) - Installation status and logs.
*   **Next Stage:** Automatically proceeds to Stage 4 (github).

### Stage 4: Pull Request Inspection
*   **Tool:** `github` (GitHub CLI)
*   **Command:** `gh api repos/owner/repo/pulls/55 --jq '.title, .state, .user.login'`
*   **Description:** Queries the GitHub API for detailed information about a specific pull request (e.g., PR #55). Extracts key fields like title, state, and author.
*   **Input:** Uses the GitHub API path and `jq` for output processing.
*   **Output:** `result` (string) - The requested details of the pull request.
*   **Next Stage:** Automatically proceeds to Stage 5 (agent-browser).

### Stage 5: Browser Binary Acquisition
*   **Tool:** `agent-browser`
*   **Command:** `install`
*   **Description:** Downloads the core browser binary (e.g., Chromium) required for automated browsing tasks in subsequent stages.
*   **Input:** Standard installation parameters.
*   **Output:** `result` (string) - Download and verification status.
*   **Next Stage:** Automatically proceeds to Stage 6 (github).

### Stage 6: Workflow Run Audit
*   **Tool:** `github` (GitHub CLI)
*   **Command:** `gh run list --repo owner/repo --limit 10`
*   **Description:** Retrieves the list of recent GitHub Actions workflow runs for the repository, providing insight into CI/CD activity.
*   **Input:** Repository target and a `limit` on the number of runs to fetch.
*   **Output:** `result` (string) - A list of workflow runs with their statuses.
*   **Next Stage:** Automatically proceeds to Stage 7 (agent-browser).

### Stage 7: Final Web Verification
*   **Tool:** `agent-browser`
*   **Command:** `open https://example.com`
*   **Description:** Performs a final web probe, potentially to verify a state change, collect updated data, or confirm the success of operations simulated in earlier stages. This closes the loop on the web monitoring aspect.
*   **Input:** Accepts various parameters for browser control.
*   **Output:** `result` (string) - The final web content retrieved.
*   **Next Stage:** The pipeline cycle completes. Data is finalized for this iteration, and the pipeline automatically restarts from **Stage 1** for continuous operation.

---
**Note:** This tool is for authorized security research and red team testing only.
```