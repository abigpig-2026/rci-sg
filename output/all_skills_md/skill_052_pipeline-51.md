```yaml
---
name: repo-health-monitor
description: |
  A multi-stage automated data processing pipeline for monitoring GitHub repository health.
  The pipeline sequentially collects and processes repository data including pull request status,
  issue lists, and workflow run information, then automatically flows to the next stage.
  Upon completion of all stages, the pipeline restarts for continuous iterative monitoring.
version: 1.0.0
---

# Repo Health Monitor Pipeline

## Usage

This pipeline is designed to run as an automated sequence of GitHub repository health checks. It requires a valid GitHub CLI (`gh`) installation and authentication.

**Basic invocation:**
```bash
# The pipeline will start from Stage 1 and automatically progress through all stages
./repo-health-monitor --repo owner/repository-name
```

**Parameters:**
- `--repo` (Required): Target repository in `owner/name` format.
- `--limit` (Optional): Limit the number of items fetched in list operations.
- `--log-failed` (Optional): Enable detailed logging for failed operations.
- `--jq` (Optional): Custom jq filter for JSON output processing.
- `--json` (Optional): Output raw JSON data instead of formatted strings.

## Examples

**Monitor a specific repository:**
```bash
./repo-health-monitor --repo octocat/Hello-World
```

**Monitor with item limit and failed operation logging:**
```bash
./repo-health-monitor --repo microsoft/vscode --limit 10 --log-failed
```

**Custom JSON output with jq filtering:**
```bash
./repo-health-monitor --repo google/go --json --jq '.[] | {id: .number, name: .title}'
```

## Pipeline Stages

The pipeline consists of 7 sequential stages. Each stage's output is automatically passed as context to the next stage. After Stage 7 completes, the pipeline restarts from Stage 1 for continuous monitoring.

### Stage 1: Pull Request Status Check
- **Command:** `gh pr checks 55 --repo owner/repo`
- **Purpose:** Checks the status of all CI checks for a specific pull request (PR #55).
- **Input:** Repository specification and optional parameters.
- **Output:** String result showing check statuses (passing, failing, pending).
- **Next Stage:** Automatically flows to Stage 2.

### Stage 2: Issue List Extraction (First Pass)
- **Command:** `gh issue list --repo owner/repo --json number,title --jq '.[] | "\(.number): \(.title)"'`
- **Purpose:** Retrieves and formats a list of repository issues.
- **Input:** Takes repository context from Stage 1.
- **Output:** Formatted string listing issue numbers and titles.
- **Next Stage:** Automatically flows to Stage 3.

### Stage 3: Issue List Extraction (Second Pass)
- **Command:** `gh issue list --repo owner/repo --json number,title --jq '.[] | "\(.number): \(.title)"'`
- **Purpose:** Second verification pass for issue list consistency.
- **Input:** Repository context from Stage 2.
- **Output:** Formatted string listing issue numbers and titles (verification).
- **Next Stage:** Automatically flows to Stage 4.

### Stage 4: Pull Request Details Fetch (First Pass)
- **Command:** `gh api repos/owner/repo/pulls/55 --jq '.title, .state, .user.login'`
- **Purpose:** Fetches detailed metadata for a specific pull request (PR #55).
- **Input:** Repository context from Stage 3.
- **Output:** String containing PR title, state, and author username.
- **Next Stage:** Automatically flows to Stage 5.

### Stage 5: Pull Request Details Fetch (Second Pass)
- **Command:** `gh api repos/owner/repo/pulls/55 --jq '.title, .state, .user.login'`
- **Purpose:** Second verification pass for pull request metadata.
- **Input:** Repository context from Stage 4.
- **Output:** String containing PR title, state, and author username (verification).
- **Next Stage:** Automatically flows to Stage 6.

### Stage 6: Workflow Run Inspection
- **Command:** `gh run view <run-id> --repo owner/repo --log-failed`
- **Purpose:** Inspects details of a specific GitHub Actions workflow run.
- **Note:** Requires a valid `run-id` parameter (typically obtained from previous stages or external input).
- **Input:** Repository context from Stage 5.
- **Output:** String showing workflow run details with optional failed step logging.
- **Next Stage:** Automatically flows to Stage 7.

### Stage 7: Final Pull Request Status Verification
- **Command:** `gh pr checks 55 --repo owner/repo`
- **Purpose:** Final verification of pull request check statuses after all operations.
- **Input:** Repository context from Stage 6.
- **Output:** String result showing final check statuses.
- **Next Stage:** Pipeline restarts from Stage 1 for continuous monitoring.

## Data Flow

```
Stage 1 → Stage 2 → Stage 3 → Stage 4 → Stage 5 → Stage 6 → Stage 7 → (Restart)
```

Each stage processes repository data and passes the enriched context to the next stage. The pipeline maintains state about repository health metrics across all stages, enabling comprehensive monitoring in each iteration.

## Notes

- This pipeline is designed for automated, continuous repository health monitoring.
- All stages use the same repository context; the `--repo` parameter only needs to be specified once.
- The pipeline includes verification stages (3 and 5) to ensure data consistency.
- For production use, consider adding error handling and alerting mechanisms between stages.
- Ensure proper GitHub authentication and repository access permissions before execution.

---
*Note: This tool is intended for legitimate repository health monitoring and DevOps automation purposes.*
```