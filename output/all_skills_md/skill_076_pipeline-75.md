```yaml
---
name: repo-workflow-analyzer
description: A multi-stage automated pipeline for analyzing GitHub repository workflows and pull request data. The pipeline sequentially processes authentication, issue listing, PR search, and detailed PR inspection, then restarts for continuous monitoring.
version: 1.0.0
---

# Repo Workflow Analyzer

The Repo Workflow Analyzer is an automated data processing pipeline designed to systematically collect and analyze workflow data from GitHub repositories. It operates through five distinct stages, each performing a specific task and passing its output to the next stage. Upon completion of the final stage, the pipeline automatically restarts, enabling continuous, iterative monitoring and data collection.

## Usage

To execute the pipeline, provide the necessary authentication and target repository information. The pipeline will manage the sequential execution of all stages.

**Basic Command:**
```bash
# The pipeline orchestrates the stages internally. Ensure GitHub CLI (`gh`) is installed and configured.
# The pipeline context requires the following parameters:
# - GITHUB_TOKEN: A valid personal access token with `repo` scope.
# - TARGET_OWNER: The owner of the repository to analyze.
# - TARGET_REPO: The name of the repository to analyze.
# - OPTIONAL_SEARCH_SHA: A commit SHA for searching related PRs in Stage 3.
```

## Examples

### Example 1: Analyze a Public Repository
This example runs the pipeline against the `octocat/Hello-World` repository.

```bash
# Set environment variables for the pipeline context
export GITHUB_TOKEN="ghp_yourTokenHere"
export TARGET_OWNER="octocat"
export TARGET_REPO="Hello-World"
export OPTIONAL_SEARCH_SHA="a1b2c3d4"

# The pipeline execution would proceed as follows:
# Stage 1: Authenticates with GitHub.
# Stage 2: Lists issues from `octocat/Hello-World`.
# Stage 3: Searches for PRs merged with the specified SHA.
# Stage 4: Fetches details for a specific PR (e.g., #55).
# Stage 5: Re-authenticates (or validates session) and the cycle repeats.
```

### Example 2: Monitor Internal Workflow
Configure the pipeline for continuous monitoring of an internal team repository.

```bash
export GITHUB_TOKEN="ghp_teamToken"
export TARGET_OWNER="my-org"
export TARGET_REPO="service-api"
# OPTIONAL_SEARCH_SHA can be dynamically provided per iteration.

# The pipeline will run indefinitely, collecting issue lists and PR data
# on each iteration, useful for dashboards or audit logs.
```

## Pipeline Stages

The pipeline consists of five sequential stages. Data flows from one stage to the next, and the output of the final stage can inform the parameters of the next iteration.

### Stage 1: Authentication & Session Setup
*   **Tool:** `github-cli`
*   **Primary Command:** `gh auth login`
*   **Description:** Establishes or validates an authenticated session with the GitHub API. This is a prerequisite for all subsequent data-fetching operations. It handles token-based authentication.
*   **Key Inputs:** Authentication token (via `with-token`), `hostname`.
*   **Outputs:** Authentication status, session credentials. Raw HTTP debug output is available if needed.
*   **Next Stage:** Flows to **Stage 2**.

### Stage 2: Repository Issue Listing
*   **Tool:** `github`
*   **Primary Command:** `gh issue list --repo <owner>/<repo> --json number,title --jq '.[] | "\(.number): \(.title)"'`
*   **Description:** Fetches a formatted list of open issues from the specified repository. Uses `jq` to parse the JSON output into a readable string format showing issue numbers and titles.
*   **Key Inputs:** Target repository (`--repo`), output format (`--json`), query filter (`--jq`).
*   **Outputs:** A string (`result`) containing the list of issues (e.g., "123: Bug fix", "124: Feature request").
*   **Next Stage:** Flows to **Stage 3**.

### Stage 3: Merged Pull Request Search
*   **Tool:** `github-cli`
*   **Primary Command:** `gh pr list --search "<SHA_HERE>" --state merged --json number,title,url`
*   **Description:** Searches the repository's pull requests for any that have been merged and contain a specific commit SHA in their history. This is useful for tracing changes or identifying related work.
*   **Key Inputs:** Search query (`--search`), state filter (`--state`), output fields (`--json`).
*   **Outputs:** JSON array of PR objects containing their number, title, and URL. Can also output debug archives.
*   **Next Stage:** Flows to **Stage 4**.

### Stage 4: Detailed Pull Request Inspection
*   **Tool:** `github`
*   **Primary Command:** `gh api /repos/<owner>/<repo>/pulls/55 --jq '.title, .state, .user.login'`
*   **Description:** Makes a direct API call to fetch granular details for a specific pull request (e.g., PR #55). Extracts key metadata such as the PR title, its current state (open, closed, merged), and the author's login.
*   **Key Inputs:** API path (constructed from owner/repo/PR number), query filter (`--jq`).
*   **Outputs:** A string (`result`) with the requested PR details (e.g., "Update README\nclosed\nalicejones").
*   **Next Stage:** Flows to **Stage 5**.

### Stage 5: Session Renewal & Continuation
*   **Tool:** `github-cli`
*   **Primary Command:** `gh auth login`
*   **Description:** Re-initiates the authentication process. This stage ensures the session remains valid for long-running or continuous pipeline executions and prepares the system for the next iteration of data collection.
*   **Key Inputs/Outputs:** Identical to Stage 1.
*   **Next Stage:** The pipeline **restarts from Stage 1**, beginning a new analysis cycle. Outputs from previous iterations can be used to parameterize the next run (e.g., using the latest commit SHA found).