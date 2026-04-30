```yaml
---
name: web-repo-sync
description: A multi-stage automated data processing pipeline that synchronizes web content with GitHub repository operations. The pipeline cycles through browser automation and GitHub API interactions in a continuous loop.
version: 1.0.0
---

# Web-Repo Sync Pipeline

## Overview

The `web-repo-sync` pipeline is an automated data processing workflow designed to orchestrate tasks between web browsing automation and GitHub repository management. It operates in a sequential, multi-stage manner, where the output of one stage automatically triggers the next. Upon completion of all stages, the pipeline resets and begins a new iteration for continuous operation.

## Usage

To execute the pipeline, invoke the primary `web-repo-sync` command. The pipeline manages its own state and data flow between stages.

```bash
# Start the pipeline
web-repo-sync
```

The pipeline will run through its defined stages (1-5) and then loop back to stage 1 to begin the next cycle.

## Examples

### Basic Execution
Run the complete pipeline cycle. The following is a simulated output showing the transition between stages.

```bash
$ web-repo-sync
[INFO] Starting web-repo-sync pipeline v1.0.0
[STAGE 1] agent-browser: Opening https://example.com...
[STAGE 1] Result: "Page loaded successfully."
[STAGE 2] github: Fetching issue list from owner/repo...
[STAGE 2] Result: "123: Sample Bug Fix\n124: Feature Request"
[STAGE 3] agent-browser: Installing with dependencies...
[STAGE 3] Result: "Installation complete."
[STAGE 4] github: Fetching Pull Request #55 details...
[STAGE 4] Result: "Update README\nopen\nalicej"
[STAGE 5] agent-browser: Opening https://example.com...
[STAGE 5] Result: "Page loaded successfully."
[INFO] Pipeline cycle complete. Restarting...
```

## Pipeline Stages

The pipeline consists of five sequential stages. Data flows unidirectionally from Stage 1 to Stage 5, after which the cycle repeats.

### Stage 1: Web Content Initialization
*   **Agent:** `agent-browser`
*   **Action:** Opens the initial target URL (`https://example.com`) to fetch or monitor web content.
*   **Input:** Accepts various parameters including `url`, `json`, `text`, and session control flags (`session`, `abort`).
*   **Output:** A `string` (`result`) containing the status or content from the page load.
*   **Next Stage:** Automatically proceeds to **Stage 2 (GitHub Issue Fetch)**.

### Stage 2: GitHub Issue Aggregation
*   **Agent:** `github`
*   **Action:** Lists recent issues from a specified GitHub repository (`owner/repo`) and formats the output.
*   **Command Simulated:** `gh issue list --repo owner/repo --json number,title --jq '.[] | "\(.number): \(.title)"'`
*   **Input:** Accepts repository target (`repo`), output format (`json`), and query filters (`jq`, `limit`).
*   **Output:** A `string` (`result`) containing a formatted list of issue numbers and titles.
*   **Next Stage:** Automatically proceeds to **Stage 3 (Browser Environment Setup)**.

### Stage 3: Dependency Installation
*   **Agent:** `agent-browser`
*   **Action:** Prepares the browser automation environment by installing necessary components, including system dependencies on Linux.
*   **Input:** Uses the `with-deps` flag alongside standard `agent-browser` parameters.
*   **Output:** A `string` (`result`) confirming the installation status.
*   **Next Stage:** Automatically proceeds to **Stage 4 (GitHub PR Inspection)**.

### Stage 4: Pull Request Data Extraction
*   **Agent:** `github`
*   **Action:** Fetches detailed information about a specific Pull Request (e.g., #55) via the GitHub API.
*   **Command Simulated:** `gh api repos/owner/repo/pulls/55 --jq '.title, .state, .user.login'`
*   **Input:** Utilizes API pathing, JSON output (`json`), and query filtering (`jq`).
*   **Output:** A `string` (`result`) containing the PR title, state, and author.
*   **Next Stage:** Automatically proceeds to **Stage 5 (Web Content Verification)**.

### Stage 5: Web Content Verification
*   **Agent:** `agent-browser`
*   **Action:** Re-opens or verifies the target URL (`https://example.com`), potentially to confirm changes or monitor state.
*   **Input:** Identical to Stage 1, accepting `url`, `json`, `text`, and control parameters.
*   **Output:** A `string` (`result`) containing the final status or content from the page.
*   **Next Stage:** The pipeline cycle completes. The output is finalized, and the pipeline **restarts from Stage 1** for the next iteration.
```