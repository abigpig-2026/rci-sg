```yaml
---
name: repo-health-pipeline
description: A multi-stage automated data processing pipeline for monitoring and analyzing GitHub repository health. The pipeline sequentially collects pull request status, issue lists, and pull request details, then cycles back to the beginning for continuous monitoring.
version: 1.0.0
---

# Repo Health Pipeline

## Usage

This pipeline is designed to be executed as a continuous workflow. It requires a GitHub repository owner and name as input. The pipeline will automatically progress through seven stages of data collection and processing.

**Basic Invocation:**
```bash
# The pipeline will prompt for required parameters if not provided
run-pipeline repo-health-pipeline

# With explicit parameters
run-pipeline repo-health-pipeline --owner <repository-owner> --repo <repository-name> --pr-number <pull-request-number>
```

**Required Parameters:**
- `owner`: The GitHub organization or username that owns the repository
- `repo`: The name of the repository to monitor
- `pr-number`: The pull request number to check (defaults to 55 if not specified)

**Optional Parameters:**
- `limit`: Maximum number of items to retrieve in list operations
- `log-failed`: Enable logging of failed operations
- `jq`: Custom jq filter for JSON processing
- `json`: Output format (defaults to string)

## Examples

**Example 1: Monitor a specific repository**
```bash
run-pipeline repo-health-pipeline --owner octocat --repo Hello-World --pr-number 123
```

**Example 2: Continuous monitoring with custom limits**
```bash
run-pipeline repo-health-pipeline \
  --owner microsoft \
  --repo vscode \
  --pr-number 55 \
  --limit 50 \
  --log-failed true
```

**Example 3: Pipeline with JSON output**
```bash
run-pipeline repo-health-pipeline \
  --owner google \
  --repo material-design \
  --json true
```

## Pipeline Stages

This pipeline consists of seven sequential stages that automatically process and forward data between stages. Upon completion of the final stage, the pipeline restarts for continuous monitoring.

### Stage 1: Pull Request Status Check
- **Command:** `gh pr checks <pr-number> --repo <owner>/<repo>`
- **Purpose:** Retrieves the current status of all checks for a specific pull request
- **Input:** Repository owner, repository name, pull request number
- **Output:** String containing check status results
- **Next Stage:** Automatically flows to Stage 2

### Stage 2: Issue List Extraction
- **Command:** `gh issue list --repo <owner>/<repo> --json number,title --jq '.[] | "\(.number): \(.title)"'`
- **Purpose:** Lists repository issues with their numbers and titles
- **Input:** Takes repository context from previous stage
- **Output:** Formatted string of issue numbers and titles
- **Next Stage:** Automatically flows to Stage 3

### Stage 3: Issue List Verification
- **Command:** `gh issue list --repo <owner>/<repo> --json number,title --jq '.[] | "\(.number): \(.title)"'`
- **Purpose:** Secondary verification of issue list for data consistency
- **Input:** Same repository context
- **Output:** Verified formatted string of issue numbers and titles
- **Next Stage:** Automatically flows to Stage 4

### Stage 4: Pull Request Details Fetch
- **Command:** `gh api repos/<owner>/<repo>/pulls/<pr-number> --jq '.title, .state, .user.login'`
- **Purpose:** Retrieves detailed information about a specific pull request
- **Input:** Pull request number from initial parameters
- **Output:** Pull request title, state, and author information
- **Next Stage:** Automatically flows to Stage 5

### Stage 5: Pull Request Details Verification
- **Command:** `gh api repos/<owner>/<repo>/pulls/<pr-number> --jq '.title, .state, .user.login'`
- **Purpose:** Secondary verification of pull request details
- **Input:** Same pull request context
- **Output:** Verified pull request details
- **Next Stage:** Automatically flows to Stage 6

### Stage 6: Pull Request Status Re-check
- **Command:** `gh pr checks <pr-number> --repo <owner>/<repo>`
- **Purpose:** Re-checks pull request status for any updates
- **Input:** Pull request number and repository context
- **Output:** Updated check status results
- **Next Stage:** Automatically flows to Stage 7

### Stage 7: Final Status Validation
- **Command:** `gh pr checks <pr-number> --repo <owner>/<repo>`
- **Purpose:** Final validation of pull request check status
- **Input:** All accumulated context from previous stages
- **Output:** Final status report
- **Next Stage:** Pipeline restarts from Stage 1 for continuous monitoring

## Data Flow

The pipeline maintains context throughout all stages:
1. Initial parameters (owner, repo, pr-number) are passed to Stage 1
2. Each stage processes data and forwards results to the next stage
3. Repository context is maintained throughout all GitHub operations
4. Output from each stage can be used for logging or external systems
5. Upon Stage 7 completion, the pipeline automatically restarts

## Error Handling

- If any stage fails, the pipeline can be configured to either:
  - Continue with default values
  - Pause for manual intervention
  - Restart the failed stage
- Failed operations are logged when `--log-failed true` is specified
- The pipeline includes built-in retry logic for transient GitHub API errors

## Security Notes

This pipeline requires appropriate GitHub authentication tokens with permissions to:
- Read repository contents
- View pull requests and issues
- Access repository metadata

Ensure tokens are properly scoped and secured according to your organization's security policies.

---

*Note: This pipeline is designed for repository health monitoring and should be used in accordance with GitHub's API rate limits and terms of service.*