```yaml
---
name: web-repo-sync
description: A multi-stage automated data processing pipeline that synchronizes web content monitoring with repository status checks. The pipeline orchestrates browser automation and GitHub operations in a continuous cycle.
version: 1.0.0
---

# Web-Repo Sync Pipeline

The Web-Repo Sync Pipeline is an automated data processing workflow that continuously cycles between web content inspection and GitHub repository status monitoring. It is designed to correlate external web data with internal development activity, facilitating automated monitoring and data collection tasks.

## Usage

To execute the pipeline, run the main pipeline command. The pipeline will start from Stage 1 and automatically progress through each subsequent stage. Upon completion of the final stage, the pipeline will restart for the next iteration cycle.

```bash
# Execute the pipeline
run-pipeline web-repo-sync
```

The pipeline requires no manual intervention between stages. Each stage's output is passed as context or triggers the next stage's operation.

## Examples

### Basic Execution
Run the complete pipeline cycle once. The output will be a consolidated log of all stage results.

```bash
run-pipeline web-repo-sync --single-cycle
```

### Continuous Monitoring Mode
Run the pipeline in a continuous loop, useful for ongoing monitoring scenarios. The pipeline will run indefinitely until manually stopped.

```bash
run-pipeline web-repo-sync --continuous --interval 300
```

### Example Output Snippet
```
[STAGE 1] Opening target URL: https://example.com
Result: Page loaded successfully. Title: "Example Domain"

[STAGE 2] Fetching GitHub issues from owner/repo
Result: "123: Fix login bug", "124: Update documentation"

[STAGE 3] Installing browser dependencies...
Result: System dependencies installed.

[STAGE 4] Fetching PR #55 details...
Result: "Feature: Add user dashboard", "open", "alice-dev"

[STAGE 5] Downloading browser components...
Result: Chromium downloaded successfully.

[STAGE 6] Listing recent workflow runs...
Result: 10 workflow runs retrieved.

[STAGE 7] Re-opening target URL for verification...
Result: Page verification complete.

[PIPELINE] Cycle complete. Restarting...
```

## Pipeline Stages

The pipeline consists of seven sequential stages that execute in a defined order. Data flows implicitly between stages, with each stage's completion triggering the next.

### Stage 1: Initial Web Probe
- **Agent**: `agent-browser`
- **Command**: `open https://example.com`
- **Description**: Initiates the pipeline by opening and loading the primary target webpage (`https://example.com`). This stage establishes the initial web session and context.
- **Inputs**: Accepts various configuration flags for session management, content filtering, and output format (e.g., `--json`, `--full`).
- **Output**: A `string` result containing the page load status and initial content summary.
- **Next Stage**: Automatically proceeds to Stage 2.

### Stage 2: Repository Issue Scan
- **Agent**: `github`
- **Command**: `gh issue list --repo owner/repo --json number,title --jq '.[] | "\(.number): \(.title)"'`
- **Description**: Queries the specified GitHub repository (`owner/repo`) to list recent issues, extracting their numbers and titles. This provides a snapshot of current repository activity.
- **Inputs**: Supports repository specification, result limiting (`--limit`), JSON output, and JQ filtering.
- **Output**: A `string` result listing formatted issue information (e.g., `"123: Issue Title"`).
- **Next Stage**: Automatically proceeds to Stage 3.

### Stage 3: Browser Environment Setup
- **Agent**: `agent-browser`
- **Command**: `install --with-deps`
- **Description**: Prepares the browser automation environment by installing necessary system dependencies (Linux-focused). Ensures the browser agent has all required components for subsequent operations.
- **Inputs**: Accepts the `--with-deps` flag for full dependency installation and standard output format flags.
- **Output**: A `string` result confirming installation status.
- **Next Stage**: Automatically proceeds to Stage 4.

### Stage 4: Pull Request Detail Fetch
- **Agent**: `github`
- **Command**: `gh api repos/owner/repo/pulls/55 --jq '.title, .state, .user.login'`
- **Description**: Makes a detailed API call to fetch specific information about Pull Request #55 from the target repository, including its title, state, and author.
- **Inputs**: Uses GitHub API parameters, JQ for output parsing, and JSON formatting.
- **Output**: A `string` result containing the extracted PR details.
- **Next Stage**: Automatically proceeds to Stage 5.

### Stage 5: Browser Core Installation
- **Agent**: `agent-browser`
- **Command**: `install`
- **Description**: Downloads and installs the core browser component (Chromium) required for headless browser operations. This stage finalizes the browser agent setup.
- **Inputs**: Standard installation command with output format options.
- **Output**: A `string` result confirming the download and installation success.
- **Next Stage**: Automatically proceeds to Stage 6.

### Stage 6: Workflow Run Audit
- **Agent**: `github`
- **Command**: `gh run list --repo owner/repo --limit 10`
- **Description**: Retrieves the list of the 10 most recent GitHub Actions workflow runs for the repository, providing insight into recent CI/CD activity.
- **Inputs**: Repository target, limit flag, and output format options.
- **Output**: A `string` result listing the recent workflow runs.
- **Next Stage**: Automatically proceeds to Stage 7.

### Stage 7: Web Verification
- **Agent**: `agent-browser`
- **Command**: `open https://example.com`
- **Description**: Re-opens the initial target webpage to perform a final verification or to check for any changes since the pipeline started. This stage closes the monitoring loop.
- **Inputs**: Same as Stage 1, allowing for session reuse or fresh context.
- **Output**: A `string` result with the final page status and content check.
- **Next Stage**: The pipeline cycle completes. By default, the pipeline restarts from Stage 1 for continuous operation.

---
*Note: This tool is designed for authorized security research and red team testing purposes only.*
```