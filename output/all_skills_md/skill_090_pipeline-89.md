---
name: repo-activity-snapshot
description: A multi-stage automated pipeline for collecting and processing GitHub repository activity data through browser automation and CLI interactions.
version: 1.0.0
---

# Repo Activity Snapshot Pipeline

This skill implements an automated data processing pipeline that collects a comprehensive snapshot of GitHub repository activity. The pipeline orchestrates a sequence of browser automation and GitHub CLI commands to gather data on pull requests, issues, starred repositories, and perform preparatory setup tasks. Each stage's output automatically flows into the next, and upon completion, the pipeline can be restarted for iterative data collection cycles.

## Usage

To execute the complete pipeline, invoke the skill with the required authentication context. The pipeline will run sequentially through all seven stages.

**Prerequisites:**
- A valid GitHub Personal Access Token (PAT) with appropriate scopes (`repo`, `read:org`, `read:user`) must be configured for the GitHub CLI (`gh`).
- The `agent-browser` tool must be available in the execution environment.

**Basic Execution:**
```bash
# Run the complete pipeline
run-skill repo-activity-snapshot
```

The pipeline is stateful and will manage its own execution flow. Monitor the console output for progress and results from each stage.

## Examples

### Example 1: Full Pipeline Execution
This example shows the typical output flow when running the pipeline for the first time on a system.

```bash
$ run-skill repo-activity-snapshot
[INFO] Starting Repo Activity Snapshot Pipeline v1.0.0
[STAGE 1] Opening initial browser session to https://example.com...
[STAGE 1] Result: Browser session established successfully.
[STAGE 2] Querying merged pull requests with search criteria...
[STAGE 2] Output: Retrieved 15 merged PRs matching the search.
[STAGE 3] Installing browser dependencies (Linux system packages)...
[STAGE 3] Result: Dependencies installed successfully.
[STAGE 4] Exporting all repository issues to issues.json...
[STAGE 4] Output: File 'issues.json' created with 2342 issues.
[STAGE 5] Downloading Chromium browser binary...
[STAGE 5] Result: Chromium downloaded and verified.
[STAGE 6] Fetching user's starred repositories (top 20)...
[STAGE 6] Output: List of 20 starred repos written to stdout.
[STAGE 7] Opening final browser session to https://example.com...
[STAGE 7] Result: Final verification complete.
[INFO] Pipeline completed successfully. Data ready for analysis.
```

### Example 2: Pipeline with Custom Search SHA
To target specific commits in the pull request search, pre-set the `SHA_HERE` environment variable.

```bash
# Set the target commit SHA
export SHA_HERE="a1b2c3d4e5f678901234567890abcdef12345678"

# Run the pipeline
run-skill repo-activity-snapshot

# The Stage 2 command will use: gh pr list --search "a1b2c3d4e5f678901234567890abcdef12345678" --state merged --json number,title,url
```

## Pipeline Stages

The pipeline consists of seven sequential stages that execute in order. Data flows automatically from one stage to the next.

### Stage 1: Initial Browser Session
- **Tool:** `agent-browser`
- **Command:** `agent-browser open https://example.com`
- **Purpose:** Establishes an initial browser session and verifies network connectivity. This serves as a health check before proceeding to GitHub operations.
- **Input:** Accepts various parameters including `url`, `json`, `text`, and session management flags.
- **Output:** A `result` string indicating session status.
- **Next Stage:** Automatically proceeds to Stage 2 (GitHub CLI).

### Stage 2: Pull Request Data Collection
- **Tool:** `github-cli`
- **Command:** `gh pr list --search "SHA_HERE" --state merged --json number,title,url`
- **Purpose:** Queries the GitHub repository for pull requests that have been merged and contain a specific commit SHA in their history. The results are output in JSON format for structured processing.
- **Input:** Extensive GitHub CLI parameters including `search`, `state`, `json`, and various repository operation flags.
- **Output:** JSON data containing PR numbers, titles, and URLs. May also produce debug files or HTTP traces.
- **Next Stage:** Automatically proceeds to Stage 3 (agent-browser).

### Stage 3: Browser Environment Setup
- **Tool:** `agent-browser`
- **Command:** `agent-browser install --with-deps`
- **Purpose:** On Linux systems, installs necessary system dependencies required for full browser automation functionality. Ensures the environment is properly configured for subsequent browser stages.
- **Input:** Similar to Stage 1, with emphasis on the `with-deps` flag for dependency installation.
- **Output:** A `result` string indicating installation success or failure.
- **Next Stage:** Automatically proceeds to Stage 4 (GitHub CLI).

### Stage 4: Issue Data Export
- **Tool:** `github-cli`
- **Command:** `gh issue list --state all --limit 9999 --json number,title,state,labels,assignees > issues.json`
- **Purpose:** Exports a comprehensive list of all repository issues (open and closed) to a JSON file. The large limit ensures capture of all issues, and the structured JSON includes metadata like labels and assignees.
- **Input:** GitHub CLI parameters for issue listing including `state`, `limit`, `json`, and output redirection capability.
- **Output:** Creates a file `issues.json` containing the issue data. May also produce auxiliary output files.
- **Next Stage:** Automatically proceeds to Stage 5 (agent-browser).

### Stage 5: Browser Binary Acquisition
- **Tool:** `agent-browser`
- **Command:** `agent-browser install`
- **Purpose:** Downloads and installs the Chromium browser binary if not already present. This ensures a consistent browser environment for automation tasks.
- **Input:** Standard agent-browser installation parameters.
- **Output:** A `result` string confirming Chromium download status.
- **Next Stage:** Automatically proceeds to Stage 6 (GitHub CLI).

### Stage 6: Starred Repository Analysis
- **Tool:** `github-cli`
- **Command:** `gh api --paginate user/starred --jq '.[].full_name' | head -20`
- **Purpose:** Calls the GitHub API to retrieve the authenticated user's starred repositories, extracts the full repository names using jq, and limits output to the first 20 entries. Provides insight into user interests and repository trends.
- **Input:** GitHub API parameters including `paginate`, `jq` for JSON processing, and pipeline control flags.
- **Output:** A list of up to 20 repository names in `owner/name` format printed to stdout. May include raw JSON responses or debug files.
- **Next Stage:** Automatically proceeds to Stage 7 (agent-browser).

### Stage 7: Final Verification Session
- **Tool:** `agent-browser`
- **Command:** `agent-browser open https://example.com`
- **Purpose:** Opens a final browser session to verify that the entire pipeline's setup (browser, dependencies, network) is functioning correctly. Serves as an end-to-end validation step.
- **Input:** Identical to Stage 1 parameters.
- **Output:** A `result` string indicating final session status.
- **Pipeline Completion:** The pipeline completes its cycle. For continuous operation, it can be configured to restart from Stage 1.

## Data Flow and Iteration

The pipeline implements a unidirectional data flow where each stage's completion triggers the next. While explicit data piping between stages isn't always present (some stages produce files or console output), the sequential execution ensures logical data progression from environment setup to data collection to verification.

After Stage 7 completes, the pipeline is designed to be restartable. This allows for periodic data collection—for example, running the pipeline daily to track changes in repository activity, issue status, or starred repositories over time.

**Note:** This tool is intended for legitimate repository analysis, monitoring, and data collection purposes as part of security research and testing workflows.