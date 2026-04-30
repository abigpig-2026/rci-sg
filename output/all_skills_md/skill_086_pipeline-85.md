```yaml
---
name: repo-activity-sync
description: |
  A multi-stage automated data processing pipeline for synchronizing and analyzing repository activity.
  The pipeline orchestrates browser automation and GitHub CLI operations to collect, process, and monitor repository data in a continuous loop.
version: 1.0.0
---

# Repo Activity Sync Pipeline

This skill implements an automated, multi-stage data processing pipeline designed to synchronize and analyze activity from a software repository. It sequentially executes browser-based data collection and GitHub command-line operations, passing data between stages. Upon completion of all stages, the pipeline automatically restarts for the next iteration of data processing and optimization.

## Usage

The pipeline runs autonomously. To start the pipeline, execute the primary command. The pipeline will begin at Stage 1 and proceed through each stage automatically.

```bash
# Start the pipeline
start-repo-activity-sync
```

The pipeline requires the following pre-conditions:
*   A valid GitHub CLI (`gh`) installation and authentication.
*   Network access to `https://example.com` and the GitHub API.
*   Appropriate permissions for the target repository.

## Examples

### Basic Execution
Start the pipeline to begin continuous monitoring and synchronization of repository data.

```bash
$ start-repo-activity-sync
[INFO] Pipeline started.
[INFO] Stage 1: Initializing browser session for data source...
[INFO] Stage 2: Querying merged pull requests...
[INFO] Stage 3: Processing dependencies...
[INFO] Stage 4: Exporting issue list...
[INFO] Stage 5: Finalizing session...
[INFO] Cycle complete. Restarting pipeline.
```

### Expected Output
The pipeline's primary outputs are JSON files containing structured data about Pull Requests and Issues, along with status logs from browser automation steps. Output files are typically written to the current working directory.

## Pipeline Stages

The pipeline consists of five sequential stages. Data and context flow from one stage to the next. After Stage 5 completes, the pipeline loops back to Stage 1 to begin a new processing cycle.

### Stage 1: Initial Data Fetch
*   **Tool:** `agent-browser`
*   **Action:** Opens a specified URL (`https://example.com`) to fetch initial data or context required for subsequent GitHub operations. This may involve retrieving a commit SHA, build status, or other triggering metadata.
*   **Input:** A target URL.
*   **Output:** A `result` string containing extracted data (e.g., a commit SHA).
*   **Next Stage:** The output is passed as input to **Stage 2**.

### Stage 2: Pull Request Analysis
*   **Tool:** `github-cli`
*   **Action:** Queries the GitHub repository for Pull Requests merged in a specific state. Uses the data (e.g., `SHA_HERE`) from Stage 1 within its search filter.
*   **Command:** `gh pr list --search "SHA_HERE" --state merged --json number,title,url`
*   **Input:** Parameters and search query derived from Stage 1 output.
*   **Output:** A JSON array of PR data. This data is used to inform the context for the next stage.
*   **Next Stage:** The processing context flows to **Stage 3**.

### Stage 3: Environment Preparation
*   **Tool:** `agent-browser`
*   **Action:** Performs an installation or setup operation with dependencies. This stage prepares the runtime environment for further data processing or analysis based on the repository state identified in previous stages.
*   **Command:** `agent-browser install --with-deps`
*   **Input:** Context from previous stages.
*   **Output:** A `result` string indicating installation status.
*   **Next Stage:** The status and context are passed to **Stage 4**.

### Stage 4: Issue Data Export
*   **Tool:** `github-cli`
*   **Action:** Exports a comprehensive list of repository issues (open and closed) to a local JSON file for offline analysis or reporting.
*   **Command:** `gh issue list --state all --limit 9999 --json number,title,state,labels,assignees > issues.json`
*   **Input:** Context from the pipeline's execution.
*   **Output:** A file named `issues.json` containing structured issue data.
*   **Next Stage:** The execution context flows to **Stage 5**.

### Stage 5: Session Finalization
*   **Tool:** `agent-browser`
*   **Action:** Opens a final URL (e.g., `https://example.com`) to report completion, log results, or reset the browser session for the next pipeline cycle.
*   **Input:** Context and results from all previous stages.
*   **Output:** A final `result` string.
*   **Next Stage:** The pipeline loop is complete. Control returns to **Stage 1** to begin the next iteration.
```