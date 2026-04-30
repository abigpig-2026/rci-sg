```yaml
---
name: web-repo-sync
description: |
  A multi-stage automated data processing pipeline that synchronizes web content monitoring with GitHub repository operations.
  The pipeline orchestrates browser automation and GitHub CLI commands in a sequential workflow, automatically passing data between stages.
  After completing all stages, the pipeline restarts for continuous iteration and optimization.
version: 1.0.0
---

# Web Repository Synchronization Pipeline

This skill implements an automated data processing pipeline that performs a sequence of web browser automation and GitHub repository operations. The pipeline executes seven stages in order, with the output of each stage automatically passed as context to the next. Upon completion, the pipeline can be configured to restart for continuous monitoring and synchronization tasks.

## Usage

To execute the complete pipeline:

```bash
# Run the entire pipeline from start to finish
run-pipeline web-repo-sync

# Run with specific iteration count (e.g., 3 complete cycles)
run-pipeline web-repo-sync --iterations 3

# Run with custom parameters for specific stages
run-pipeline web-repo-sync --params '{"target_url": "https://custom.example.com", "github_repo": "owner/custom-repo"}'
```

The pipeline will execute sequentially through all seven stages. Progress and results from each stage are logged and can be exported for analysis.

## Examples

### Basic Pipeline Execution
```bash
# Execute a single iteration of the pipeline
$ run-pipeline web-repo-sync
[INFO] Starting web-repo-sync pipeline
[INFO] Stage 1: Opening target webpage...
[INFO] Stage 2: Fetching GitHub issues...
[INFO] Stage 3: Installing browser dependencies...
[INFO] Stage 4: Retrieving pull request details...
[INFO] Stage 5: Downloading browser components...
[INFO] Stage 6: Checking PR status...
[INFO] Stage 7: Verifying webpage content...
[INFO] Pipeline completed successfully
```

### Continuous Monitoring Mode
```bash
# Run pipeline continuously with 5-minute intervals
$ run-pipeline web-repo-sync --continuous --interval 300
[INFO] Starting continuous web-repo-sync pipeline
[INFO] Iteration 1: Beginning at 2024-01-15T10:00:00Z
[INFO] Iteration 1: Completed at 2024-01-15T10:02:15Z
[INFO] Next iteration scheduled in 5 minutes...
```

### Pipeline with Custom Configuration
```bash
# Execute with custom target and repository
$ run-pipeline web-repo-sync \
  --params '{
    "stage1_url": "https://status.example.com",
    "stage2_repo": "organization/production-repo",
    "stage4_pr_number": 123,
    "stage6_pr_number": 123
  }'
```

## Pipeline Stages

### Stage 1: Webpage Initialization
- **Tool**: `agent-browser`
- **Command**: `open https://example.com`
- **Input**: Accepts various parameters including URL, JSON data, text content, and session management options
- **Output**: String result containing webpage content or status
- **Purpose**: Initializes browser session and loads target webpage for content monitoring
- **Next Stage**: Automatically flows to Stage 2 (GitHub Issues Fetch)

### Stage 2: Repository Issues Fetch
- **Tool**: `github` (GitHub CLI)
- **Command**: `gh issue list --repo owner/repo --json number,title --jq '.[] | "\(.number): \(.title)"'`
- **Input**: Repository specification, output formatting options (JSON, jq filter)
- **Output**: Formatted list of repository issues
- **Purpose**: Retrieves current issues from specified GitHub repository
- **Next Stage**: Automatically flows to Stage 3 (Browser Setup)

### Stage 3: Browser Environment Setup
- **Tool**: `agent-browser`
- **Command**: `install --with-deps`
- **Input**: Installation parameters including dependency management options
- **Output**: Installation status and result
- **Purpose**: Ensures browser environment is properly configured with system dependencies
- **Next Stage**: Automatically flows to Stage 4 (PR Details Retrieval)

### Stage 4: Pull Request Analysis
- **Tool**: `github` (GitHub CLI)
- **Command**: `gh api repos/owner/repo/pulls/55 --jq '.title, .state, .user.login'`
- **Input**: API endpoint specification with jq filtering
- **Output**: Key details about specific pull request (title, state, author)
- **Purpose**: Analyzes specific pull request for monitoring purposes
- **Next Stage**: Automatically flows to Stage 5 (Browser Component Update)

### Stage 5: Browser Component Management
- **Tool**: `agent-browser`
- **Command**: `install`
- **Input**: Installation parameters for browser components
- **Output**: Download and installation status
- **Purpose**: Updates or installs browser components (e.g., Chromium)
- **Next Stage**: Automatically flows to Stage 6 (PR Status Verification)

### Stage 6: PR Status Check
- **Tool**: `github` (GitHub CLI)
- **Command**: `gh pr checks 55 --repo owner/repo`
- **Input**: Pull request number and repository specification
- **Output**: Status of checks on the specified pull request
- **Purpose**: Verifies the current status and checks of a pull request
- **Next Stage**: Automatically flows to Stage 7 (Webpage Verification)

### Stage 7: Webpage Content Verification
- **Tool**: `agent-browser`
- **Command**: `open https://example.com`
- **Input**: URL and content loading parameters
- **Output**: Final webpage content or verification result
- **Purpose**: Final verification of webpage content, completing the synchronization cycle
- **Next Stage**: Pipeline restarts from Stage 1 for next iteration

## Data Flow

The pipeline implements a unidirectional data flow where each stage's output becomes available as context for subsequent stages:

```
Stage 1 (Web Init) → Stage 2 (Issues) → Stage 3 (Browser Setup) → 
Stage 4 (PR Analysis) → Stage 5 (Component Mgmt) → Stage 6 (PR Check) → 
Stage 7 (Web Verify) → [Restart to Stage 1]
```

Each stage receives:
1. Explicit parameters configured for that stage
2. Implicit context from previous stage outputs
3. Global pipeline configuration parameters

## Configuration Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `stage1_url` | URL | `https://example.com` | Target webpage URL for Stages 1 and 7 |
| `stage2_repo` | String | `owner/repo` | GitHub repository for issue listing |
| `stage4_pr_number` | Integer | `55` | Pull request number for detailed analysis |
| `stage6_pr_number` | Integer | `55` | Pull request number for status checks |
| `iteration_count` | Integer | `1` | Number of complete pipeline cycles to execute |
| `continuous_mode` | Boolean | `false` | Whether to run pipeline continuously |
| `interval_seconds` | Integer | `300` | Interval between iterations in continuous mode |

## Output Format

The pipeline produces structured output in JSON format:

```json
{
  "pipeline": "web-repo-sync",
  "iteration": 1,
  "start_time": "2024-01-15T10:00:00Z",
  "end_time": "2024-01-15T10:02:15Z",
  "stages": [
    {
      "stage": 1,
      "tool": "agent-browser",
      "command": "open https://example.com",
      "status": "success",
      "output": "Page loaded successfully",
      "duration_ms": 1250
    },
    // ... additional stage results
  ],
  "summary": {
    "total_stages": 7,
    "successful_stages": 7,
    "failed_stages": 0,
    "total_duration_ms": 135000
  }
}
```

## Error Handling

The pipeline includes robust error handling:
- **Stage Failure**: If a stage fails, the pipeline can be configured to either halt or continue with degraded functionality
- **Retry Logic**: Configurable retry attempts for transient failures
- **Context Preservation**: Failed stages preserve context for debugging purposes
- **Graceful Degradation**: Pipeline can continue with available data when non-critical stages fail

## Use Cases

1. **Continuous Integration Monitoring**: Monitor web application status alongside repository changes
2. **DevOps Synchronization**: Keep browser testing environments synchronized with repository state
3. **Content Verification**: Verify web content consistency with repository documentation
4. **Automated Reporting**: Generate combined reports of web status and repository activity

---

**Note**: This pipeline is designed for legitimate automation and monitoring purposes. Ensure you have proper authorization for all web resources and repositories accessed by this pipeline.
```