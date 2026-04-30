```yaml
---
name: web-repo-sync
description: |
  A multi-stage automated data processing pipeline that synchronizes web content analysis with repository monitoring.
  The pipeline orchestrates browser automation and GitHub operations in a sequential workflow, with data automatically flowing between stages.
  Upon completion of all stages, the pipeline restarts for the next iteration of optimization.
version: 1.0.0
---

# Web-Repo Sync Pipeline

The `web-repo-sync` pipeline is an automated, iterative workflow designed to collect and correlate data from web sources and GitHub repositories. It executes a sequence of browser automation and repository querying tasks, passing results from one stage to the next to enable continuous monitoring and data aggregation.

## Usage

The pipeline is invoked as a single command. It will automatically execute all stages in sequence.

```bash
# Run the complete pipeline
run-pipeline web-repo-sync
```

The pipeline operates autonomously. Each stage's output becomes the implicit context for the next stage. Upon finishing the final stage, the pipeline will restart from the beginning for the next monitoring cycle.

## Examples

### Basic Execution
Run the pipeline for one full cycle of data collection and synchronization.

```bash
$ run-pipeline web-repo-sync
[INFO] Starting pipeline: web-repo-sync
[INFO] Stage 1/7: Opening initial web page... Done.
[INFO] Stage 2/7: Fetching repository issues... Done.
[INFO] Stage 3/7: Installing browser dependencies... Done.
[INFO] Stage 4/7: Querying specific pull request... Done.
[INFO] Stage 5/7: Downloading browser... Done.
[INFO] Stage 6/7: Listing recent workflow runs... Done.
[INFO] Stage 7/7: Opening final web page... Done.
[INFO] Pipeline cycle complete. Restarting for next iteration.
```

### Pipeline Output
The final output of a pipeline cycle is a consolidated string result from the last stage, which can be piped to other commands or logged.

```bash
run-pipeline web-repo-sync | tee pipeline_log.txt
```

## Pipeline Stages

The pipeline consists of seven stages that execute in a strict, predefined order. Data flows unidirectionally from Stage 1 to Stage 7.

### Stage 1: Initial Web Probe
*   **Agent:** `agent-browser`
*   **Action:** Opens a specified URL (`https://example.com`) to probe web content and establish a session.
*   **Input:** Accepts various parameters including `url`, `json`, `text`, and session controls.
*   **Output:** A `string` result containing page status or content.
*   **Next Stage:** Automatically flows to **Stage 2 (GitHub Query)**.

### Stage 2: Repository Issues Scan
*   **Agent:** `github`
*   **Action:** Lists recent issues from a target GitHub repository (`owner/repo`), formatted for clarity.
*   **Command:** `gh issue list --repo owner/repo --json number,title --jq '.[] | "\(.number): \(.title)"'`
*   **Input:** Accepts `repo`, `limit`, `jq`, and `json` parameters.
*   **Output:** A `string` result listing issue numbers and titles.
*   **Next Stage:** Automatically flows to **Stage 3 (Browser Setup)**.

### Stage 3: System Dependency Installation
*   **Agent:** `agent-browser`
*   **Action:** Installs necessary browser dependencies (simulating a Linux environment setup).
*   **Command:** `agent-browser install --with-deps`
*   **Input:** Similar to Stage 1, with emphasis on the `with-deps` flag.
*   **Output:** A `string` result confirming installation status.
*   **Next Stage:** Automatically flows to **Stage 4 (Pull Request Inspection)**.

### Stage 4: Pull Request Detail Fetch
*   **Agent:** `github`
*   **Action:** Fetches detailed metadata for a specific pull request (e.g., PR #55).
*   **Command:** `gh api repos/owner/repo/pulls/55 --jq '.title, .state, .user.login'`
*   **Input:** Uses `api` endpoint with `jq` for filtering specific fields.
*   **Output:** A `string` containing the PR title, state, and author.
*   **Next Stage:** Automatically flows to **Stage 5 (Browser Runtime Prep)**.

### Stage 5: Browser Runtime Download
*   **Agent:** `agent-browser`
*   **Action:** Downloads the core browser runtime (e.g., Chromium) to prepare for further automation.
*   **Command:** `agent-browser install`
*   **Input:** Standard browser agent parameters.
*   **Output:** A `string` result confirming download success.
*   **Next Stage:** Automatically flows to **Stage 6 (Workflow Run Audit)**.

### Stage 6: CI/CD Workflow Check
*   **Agent:** `github`
*   **Action:** Lists recent workflow runs from the repository to monitor CI/CD status.
*   **Command:** `gh run list --repo owner/repo --limit 10`
*   **Input:** Takes `repo`, `limit`, and formatting parameters.
*   **Output:** A `string` listing the last 10 workflow runs.
*   **Next Stage:** Automatically flows to **Stage 7 (Final Web Verification)**.

### Stage 7: Final Web Verification
*   **Agent:** `agent-browser`
*   **Action:** Opens a final URL (`https://example.com`) to verify web accessibility or check for updates, completing the data cycle.
*   **Input:** Identical to Stage 1.
*   **Output:** A final `string` result, representing the output of the completed pipeline cycle.
*   **Next Stage:** Pipeline resets, flowing back to **Stage 1** for the next iteration.

---
*Note: This tool is designed for automated data synchronization and monitoring tasks in development and research environments.*
```