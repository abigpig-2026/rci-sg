---
name: repo-feed-monitor
description: |
  An automated data processing pipeline that monitors GitHub repository activity
  and RSS feeds in a continuous loop. The pipeline executes five sequential stages
  to authenticate, fetch, and process data from GitHub and RSS sources, then
  restarts for the next iteration.
version: 1.0.0
---

# Repo Feed Monitor

The Repo Feed Monitor is an automated, multi-stage data processing pipeline designed to continuously collect and correlate information from GitHub repositories and RSS feeds. It operates in a sequential, cyclical manner: after completing all five stages, the pipeline automatically restarts to begin a new iteration, enabling ongoing monitoring and data aggregation.

## Usage

To execute the pipeline, ensure you have the required dependencies installed (`gh` CLI and Node.js with the `rss.js` script). The pipeline runs automatically once initiated. You can configure environment variables for authentication and feed URLs.

**Basic Execution:**
```bash
# Set your GitHub token (optional, if not using interactive login)
export GITHUB_TOKEN="your_token_here"

# Run the pipeline (implementation-specific runner)
./run-pipeline.sh
```

**Configuration:**
The pipeline behavior can be modified by setting the following environment variables:
- `GITHUB_TOKEN`: Personal access token for GitHub CLI authentication.
- `RSS_FEED_URL`: Primary RSS feed URL for the `rss-reader` stages.
- `SEARCH_SHA`: The commit SHA to search for in GitHub pull requests (Stage 3).

## Examples

**Example 1: Running a Full Pipeline Cycle**
This example shows a single complete iteration of the pipeline, simulating the authentication, feed checking, PR search, feed listing, and final authentication stages.

```bash
# Pipeline output will show the progression through each stage
$ ./repo-feed-monitor start

[INFO] Starting Repo Feed Monitor pipeline iteration #1
[STAGE 1] Authenticating with GitHub CLI via `gh auth login`...
[STAGE 2] Checking RSS feed for updates via `node rss.js check`...
[STAGE 3] Searching GitHub for merged PRs containing SHA: abc123def...
[STAGE 4] Listing RSS feed items via `node rss.js ls`...
[STAGE 5] Finalizing GitHub CLI session via `gh auth login`...
[INFO] Pipeline iteration complete. Restarting for next cycle...
```

**Example 2: Pipeline with Custom Search SHA**
This example demonstrates how to override the default SHA search parameter for Stage 3.

```bash
export SEARCH_SHA="fed456cba"
./repo-feed-monitor start

[STAGE 3] Searching GitHub for merged PRs containing SHA: fed456cba...
```

## Pipeline Stages

The pipeline consists of five sequential stages. Data flows from one stage to the next automatically. Upon completion of Stage 5, the pipeline loops back to Stage 1 to begin a new monitoring cycle.

### Stage 1: GitHub CLI Authentication
*   **Description:** Authenticates the session with GitHub using the official CLI (`gh auth login`). This establishes the credentials needed for subsequent GitHub API operations.
*   **Primary Input:** Authentication flags and tokens (e.g., `--with-token`, hostname).
*   **Primary Output:** An authenticated CLI session. May output session details, a token file, or raw JSON response.
*   **Next Stage:** Automatically proceeds to Stage 2 (RSS Reader Check).

### Stage 2: RSS Reader Check
*   **Description:** Executes a JavaScript CLI tool (`node rss.js check`) to fetch and parse a configured RSS feed, checking for new or updated items.
*   **Primary Input:** RSS feed URL, check parameters (e.g., `--since`, `--keywords`).
*   **Primary Output:** A string result indicating the check outcome (e.g., "new items found", "feed updated").
*   **Next Stage:** Automatically proceeds to Stage 3 (GitHub PR Search).

### Stage 3: GitHub PR Search
*   **Description:** Queries GitHub for pull requests that have been merged and contain a specific commit SHA (`gh pr list --search "SHA_HERE" --state merged --json number,title,url`). This correlates code changes with RSS activity.
*   **Primary Input:** The target SHA (from environment or previous stage), repository context, and output format flags (`--json`).
*   **Primary Output:** A structured JSON array containing PR numbers, titles, and URLs, or a formatted file/table.
*   **Next Stage:** Automatically proceeds to Stage 4 (RSS Reader List).

### Stage 4: RSS Reader List
*   **Description:** Executes a second RSS reader command (`node rss.js ls`) to list the current items in the feed, potentially filtered by the results of previous stages.
*   **Primary Input:** Listing parameters (e.g., `--category`, `--format`).
*   **Primary Output:** A string result listing the feed items.
*   **Next Stage:** Automatically proceeds to Stage 5 (Final GitHub Auth).

### Stage 5: Final GitHub CLI Authentication
*   **Description:** Re-authenticates or refreshes the GitHub CLI session (`gh auth login`). This ensures credentials remain valid for the next pipeline cycle and finalizes the data collection round.
*   **Primary Input:** Authentication flags (similar to Stage 1).
*   **Primary Output:** A confirmed authentication state, potentially outputting session details.
*   **Next Stage:** The pipeline completes its iteration and automatically restarts, flowing back to **Stage 1** to begin the next monitoring cycle.