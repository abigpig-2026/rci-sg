```yaml
---
name: repo-activity-pipeline
description: A multi-stage automated data processing pipeline for GitHub repository activity monitoring and analysis.
version: 1.0.0
---

# Repo Activity Pipeline

An automated, multi-stage data processing pipeline designed to monitor, collect, and analyze activity within GitHub repositories. The pipeline executes a sequence of operations, automatically passing data and state between stages. Upon completion of all stages, the pipeline can be configured to restart for continuous monitoring and iterative optimization.

## Usage

The pipeline is invoked as a single command. Configuration is primarily managed through environment variables and a configuration file.

**Basic Execution:**
```bash
export GITHUB_TOKEN="your_personal_access_token"
export GITHUB_REPO="owner/repository_name"
./repo-activity-pipeline
```

**With Configuration File:**
```bash
./repo-activity-pipeline --config pipeline-config.yaml
```

**Key Environment Variables:**
*   `GITHUB_TOKEN`: (Required) A GitHub Personal Access Token with appropriate `repo` scope permissions.
*   `GITHUB_REPO`: (Required) The target repository in `owner/name` format.
*   `PIPELINE_ITERATIONS`: (Optional) Number of times to run the full pipeline loop. Default is `1`. Set to `0` for continuous run until stopped.
*   `OUTPUT_DIR`: (Optional) Directory for generated reports and JSON files. Defaults to `./pipeline_output`.

## Examples

**1. Single run for a specific repository:**
```bash
GITHUB_TOKEN="ghp_abc123" GITHUB_REPO="octocat/Hello-World" ./repo-activity-pipeline
```
This will execute all seven stages once for the `octocat/Hello-World` repo and exit.

**2. Continuous monitoring with custom output:**
```bash
export GITHUB_TOKEN="ghp_xyz789"
export GITHUB_REPO="myorg/microservice-api"
export PIPELINE_ITERATIONS=0
export OUTPUT_DIR="/var/log/github_monitor"
nohup ./repo-activity-pipeline > pipeline.log 2>&1 &
```
This runs the pipeline in a continuous loop, writing all outputs to `/var/log/github_monitor`.

**3. Using a specific commit SHA for PR search (Stage 3):**
The pipeline's third stage searches for merged Pull Requests containing a specific commit SHA. This can be pre-set:
```bash
export TARGET_SHA="a1b2c3d4e5f67890"
./repo-activity-pipeline
```
If `TARGET_SHA` is not set, the pipeline will attempt to derive a SHA from the latest successful workflow run in the repository.

## Pipeline Stages

The pipeline consists of seven sequential stages. Each stage's output (state, extracted data, or files) serves as input or context for subsequent stages.

### Stage 1: Authentication & Session Initiation
*   **Tool:** `github-cli`
*   **Primary Action:** `gh auth login`
*   **Description:** Initializes the pipeline session by authenticating with the GitHub API using the provided `GITHUB_TOKEN`. This establishes the secure context for all subsequent API calls. The stage validates token permissions and prepares the CLI environment.
*   **Input:** Authentication token (from env), various CLI configuration flags.
*   **Output:** Authenticated session state, capability to make authorized requests.
*   **Next Stage:** Flows to Stage 2 (`github`).

### Stage 2: Issue Listing & Extraction
*   **Tool:** `github`
*   **Primary Action:** `gh issue list --repo owner/repo --json number,title --jq '.[] | "\(.number): \(.title)"'`
*   **Description:** Fetches a formatted list of recent issues from the target repository. Extracts issue numbers and titles, providing a high-level overview of open work items. This data is used for initial repository assessment.
*   **Input:** Target repository, output formatting filters (`--json`, `--jq`).
*   **Output:** A formatted text string (`result`) listing issues (e.g., `"42: Bug in login flow\n43: Feature request for API"`).
*   **Next Stage:** Flows to Stage 3 (`github-cli`).

### Stage 3: Pull Request Search by Commit
*   **Tool:** `github-cli`
*   **Primary Action:** `gh pr list --search "SHA_HERE" --state merged --json number,title,url`
*   **Description:** Searches the repository's merged Pull Requests for those containing a specific commit hash (`SHA_HERE`). This identifies which features or fixes a particular commit was part of. The SHA is dynamically injected from the pipeline context (e.g., from a previous run or environment variable).
*   **Input:** Commit SHA (from context), search filters, JSON output flag.
*   **Output:** JSON array containing details (number, title, URL) of matching merged PRs. May also produce debug archives or raw HTTP logs.
*   **Next Stage:** Flows to Stage 4 (`github`).

### Stage 4: Detailed Pull Request Inspection
*   **Tool:** `github`
*   **Primary Action:** `gh api repos/owner/repo/pulls/55 --jq '.title, .state, .user.login'`
*   **Description:** Performs a detailed API query on a specific Pull Request (e.g., PR #55). Extracts key metadata such as its title, current state (open, closed, merged), and the author's login. The PR number can be derived from the results of Stage 2 or 3.
*   **Input:** Specific Pull Request number (from prior stage data), GraphQL-like query via `jq`.
*   **Output:** A string (`result`) with the extracted title, state, and author (e.g., `"Update README\nclosed\noctocat"`).
*   **Next Stage:** Flows to Stage 5 (`github-cli`).

### Stage 5: Comprehensive Issue Snapshot
*   **Tool:** `github-cli`
*   **Primary Action:** `gh issue list --state all --limit 9999 --json number,title,state,labels,assignees > issues.json`
*   **Description:** Captures a comprehensive snapshot of *all* issues (open and closed) in the repository, up to a high limit. Extends the basic list from Stage 2 by including state, labels, and assignees. Outputs this rich dataset to a JSON file for persistent storage and analysis.
*   **Input:** Repository scope, `all` state filter, extended JSON field list.
*   **Output:** A file (`issues.json`) containing a complete JSON array of issue objects. This is a primary data artifact of the pipeline.
*   **Next Stage:** Flows to Stage 6 (`github`).

### Stage 6: Workflow Run Diagnostics
*   **Tool:** `github`
*   **Primary Action:** `gh run view <run-id> --repo owner/repo --log-failed`
*   **Description:** Retrieves detailed logs for a specific GitHub Actions workflow run, with emphasis on failed steps (`--log-failed`). This is used for CI/CD pipeline health monitoring and debugging. The `run-id` is obtained from repository workflow history.
*   **Input:** Workflow run identifier, target repository, log filter flag.
*   **Output:** Diagnostic string (`result`) containing the logs of failed jobs from the specified workflow run.
*   **Next Stage:** Flows to Stage 7 (`github-cli`).

### Stage 7: Session Renewal & Continuation
*   **Tool:** `github-cli`
*   **Primary Action:** `gh auth login`
*   **Description:** Re-authenticates or refreshes the GitHub CLI session. This stage ensures long-running or iterative pipeline loops maintain a valid authentication context, handling potential token expiry or session invalidation. It resets the state for the next pipeline iteration.
*   **Input:** Authentication token.
*   **Output:** Renewed session state.
*   **Next Stage:** By default, the pipeline completes. If `PIPELINE_ITERATIONS` is set to loop, control returns to **Stage 1**, starting a new monitoring cycle.

---
*Note: This tool is designed for automated repository analytics and operational monitoring.*
```