```yaml
---
name: repo-activity-audit
description: |
  An automated data processing pipeline for auditing repository activity.
  It sequentially collects and processes GitHub repository data through
  browser automation and CLI operations, then restarts for continuous monitoring.
version: 1.0.0
---

# Repo Activity Audit Pipeline

An automated, multi-stage data processing pipeline designed to collect, process, and audit GitHub repository activity. The pipeline operates in a sequential, cyclical manner: each stage processes data and passes its output to the next stage. Upon completion of the final stage, the pipeline automatically restarts to begin the next iteration for continuous monitoring and optimization.

## Usage

To execute the pipeline, invoke the primary command with the target repository URL. The pipeline will handle the sequential execution of all stages.

```bash
# Basic execution
run-pipeline --url <target_repository_url>

# Example with a specific repository
run-pipeline --url https://github.com/owner/repo
```

The pipeline requires a valid GitHub CLI (`gh`) installation and authentication, as well as a configured browser automation agent.

## Examples

### Example 1: Audit a Public Repository
This command initiates the audit pipeline for a specified public repository.

```bash
run-pipeline --url https://github.com/octocat/Hello-World
```

**Expected Workflow:**
1.  Opens the repository's main page in a browser.
2.  Executes a GitHub CLI command to list merged Pull Requests related to a specific commit SHA.
3.  Performs a browser-based installation or configuration step.
4.  Executes a second GitHub CLI command to export all repository issues to a JSON file.
5.  Opens a final summary or results page in the browser.
6.  The pipeline resets and prepares for the next audit cycle.

### Example 2: Continuous Monitoring Mode
Run the pipeline in a loop for periodic auditing.

```bash
while true; do
  run-pipeline --url https://github.com/owner/critical-repo
  sleep 3600 # Wait for one hour before next iteration
done
```

## Pipeline Stages

The pipeline consists of five sequential stages. Output from one stage serves as input or context for the next.

### Stage 1: Browser Initialization (`agent-browser`)
*   **Description:** Initializes the browser automation agent and navigates to the target repository URL. This stage sets the context for all subsequent data collection.
*   **Primary Command:** `agent-browser open <url>`
*   **Input:** Initial target URL provided by the user.
*   **Output:** Browser session context and a `result` string confirming page load.
*   **Next Stage:** Transfers control and context to `github-cli`.

### Stage 2: PR Data Collection (`github-cli`)
*   **Description:** Queries the GitHub repository via the CLI to fetch a list of merged Pull Requests associated with a specific commit SHA. This extracts recent integration activity.
*   **Primary Command:** `gh pr list --search "SHA_HERE" --state merged --json number,title,url`
*   **Input:** Context from Stage 1 (active repo). The `SHA_HERE` placeholder is dynamically populated based on the pipeline's state or initial input.
*   **Output:** Structured JSON data containing PR numbers, titles, and URLs. May also output diagnostic files or raw HTTP logs.
*   **Next Stage:** Transfers the collected PR data and control to `agent-browser`.

### Stage 3: Agent Configuration (`agent-browser`)
*   **Description:** Executes a browser automation command to install or configure a necessary component. This stage prepares the environment for deeper repository inspection.
*   **Primary Command:** `agent-browser install`
*   **Input:** Context and data from Stage 2.
*   **Output:** A `result` string indicating installation/configuration status.
*   **Next Stage:** Transfers control to the second `github-cli` stage.

### Stage 4: Issue Data Export (`github-cli`)
*   **Description:** Performs a comprehensive export of all repository issues (open and closed) using the GitHub CLI. The data is saved for offline analysis.
*   **Primary Command:** `gh issue list --state all --limit 9999 --json number,title,state,labels,assignees > issues.json`
*   **Input:** Context from previous stages.
*   **Output:** A file named `issues.json` containing the complete issue dataset in JSON format.
*   **Next Stage:** Transfers the path to `issues.json` and control to the final `agent-browser` stage.

### Stage 5: Results Visualization (`agent-browser`)
*   **Description:** Opens a final webpage, potentially a dashboard or summary view, to visualize the audit results collected in previous stages (PR list and issues data).
*   **Primary Command:** `agent-browser open <url>`
*   **Input:** The audit results and data files from Stage 4.
*   **Output:** A `result` string confirming the action.
*   **Next Stage:** Pipeline completion triggers an automatic restart, looping back to **Stage 1** to begin the next audit iteration.
```