```yaml
---
name: repo-intelligence-pipeline
description: |
  An automated data processing pipeline that orchestrates GitHub repository intelligence gathering
  and RSS feed monitoring. The pipeline executes in sequential stages, with data flowing
  automatically between GitHub CLI operations and RSS feed checks for continuous monitoring
  and analysis.
version: 1.0.0
---

# Repo Intelligence Pipeline

## Overview

The Repo Intelligence Pipeline is a multi-stage automated workflow designed to collect, process, and monitor repository data from GitHub alongside relevant RSS feed updates. It operates as a continuous loop, executing a sequence of GitHub CLI commands and RSS feed checks, with each stage's output potentially informing the next. Upon completion of all stages, the pipeline resets for the next iteration, enabling ongoing monitoring and data aggregation.

## Usage

To execute the pipeline, ensure you have the necessary prerequisites installed and configured:

1.  **Prerequisites:**
    *   GitHub CLI (`gh`) installed and authenticated (`gh auth login`).
    *   Node.js runtime environment.
    *   The RSS reader CLI script (`rss.js`) available in your PATH or current directory.

2.  **Execution:**
    The pipeline is designed to be triggered as a single command or scheduled job. It will run through all seven stages sequentially without manual intervention.
    ```bash
    # Example: Run the pipeline once
    ./repo-intelligence-pipeline.sh

    # Example: Schedule with cron (runs every 6 hours)
    0 */6 * * * /path/to/repo-intelligence-pipeline.sh
    ```

3.  **Configuration:**
    *   Set the `GITHUB_REPO` environment variable to target a specific repository.
    *   Configure the RSS feed sources within the `rss.js` script or via its command-line arguments.

## Examples

### Basic Execution
Run the complete pipeline cycle for the current repository context.
```bash
export GITHUB_REPO="owner/repo-name"
./repo-intelligence-pipeline.sh
```

### Pipeline with Custom Output
Execute the pipeline and redirect the final aggregated output to a file.
```bash
./repo-intelligence-pipeline.sh 2>&1 | tee pipeline_output_$(date +%Y%m%d).log
```

### Simulating a Single Iteration
Manually step through the pipeline stages to verify functionality.
```bash
# Stage 1: Authenticate and initialize
gh auth status
# Stage 2: Check RSS for recent updates related to the repo
node rss.js check --keywords "$GITHUB_REPO"
# Stage 3: List merged PRs (replace SHA_HERE with an actual commit SHA from context)
gh pr list --repo "$GITHUB_REPO" --search "SHA_HERE" --state merged --json number,title,url
# ... Continue through remaining stages
```

## Pipeline Stages

The pipeline consists of seven distinct stages that execute in order. Data flows from one stage to the next, and the pipeline loops upon completion.

### Stage 1: GitHub Authentication & Context Setup
*   **Tool:** `github-cli`
*   **Command:** `gh auth login` (or status check)
*   **Purpose:** Establishes authenticated session and initializes the GitHub CLI context for subsequent operations. This ensures all following `gh` commands have the necessary permissions.
*   **Input:** Various `gh` CLI flags and options for auth configuration.
*   **Output:** Authentication token/session. Context set for target repository.
*   **Next Stage:** Proceeds to Stage 2 (RSS Reader).

### Stage 2: RSS Feed Initial Check
*   **Tool:** `rss-reader` (JS CLI)
*   **Command:** `node rss.js check`
*   **Purpose:** Performs an initial scan of configured RSS feeds. Can filter by category, keywords, or time to gather recent updates potentially relevant to the monitored repository.
*   **Input:** Command-line options like `--keywords`, `--since`, `--category`.
*   **Output:** A `result` string summarizing findings (e.g., "New updates found" or "No new items").
*   **Next Stage:** Proceeds to Stage 3 (GitHub CLI).

### Stage 3: Pull Request Analysis
*   **Tool:** `github-cli`
*   **Command:** `gh pr list --search "SHA_HERE" --state merged --json number,title,url`
*   **Purpose:** Queries the repository for pull requests merged around a specific commit SHA (which may be derived from previous context or RSS data). Extracts structured data (number, title, URL) for analysis.
*   **Input:** Search query, state filter, JSON output fields.
*   **Output:** JSON array of merged pull request data.
*   **Next Stage:** Proceeds to Stage 4 (RSS Reader).

### Stage 4: RSS Feed Listing
*   **Tool:** `rss-reader` (JS CLI)
*   **Command:** `node rss.js ls`
*   **Purpose:** Lists current items from RSS feeds, possibly using filters. This stage provides a broader view of feed content after the PR analysis, which might inform the next GitHub query.
*   **Input:** Similar options as Stage 2 (`--category`, `--format`, etc.).
*   **Output:** A `result` string listing feed items.
*   **Next Stage:** Proceeds to Stage 5 (GitHub CLI).

### Stage 5: Issue Repository Snapshot
*   **Tool:** `github-cli`
*   **Command:** `gh issue list --state all --limit 9999 --json number,title,state,labels,assignees > issues.json`
*   **Purpose:** Captures a comprehensive snapshot of all issues (open and closed) in the repository. This data is saved to a file (`issues.json`) for later review or trend analysis.
*   **Input:** State filter, high limit, specific JSON fields to extract.
*   **Output:** A JSON file (`issues.json`) containing detailed issue data.
*   **Next Stage:** Proceeds to Stage 6 (RSS Reader).

### Stage 6: RSS Feed Detailed Listing
*   **Tool:** `rss-reader` (JS CLI)
*   **Command:** `node rss.js list`
*   **Purpose:** Executes another, potentially more detailed, listing of RSS feed content. This stage acts as a final data collection point from external sources before the pipeline cycle concludes.
*   **Input:** Standard RSS reader options.
*   **Output:** A `result` string with detailed feed information.
*   **Next Stage:** Proceeds to Stage 7 (GitHub CLI).

### Stage 7: Session Refresh & Cleanup
*   **Tool:** `github-cli`
*   **Command:** `gh auth login` (or token refresh/logout)
*   **Purpose:** Refreshes the authentication session or performs cleanup. Ensures the pipeline is ready to start a new cycle securely. This stage closes the loop.
*   **Input:** Auth command parameters.
*   **Output:** Refreshed session state or confirmation of logout.
*   **Next Stage:** Pipeline loops back to **Stage 1** to begin the next iteration.

---
*Note: This tool is designed for automated repository monitoring and data aggregation. Ensure compliance with GitHub's Terms of Service and API rate limits when deploying.*
```