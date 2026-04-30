```yaml
---
name: repo-analysis-pipeline
description: |
  A multi-stage automated data processing pipeline for repository analysis and dependency management.
  The pipeline orchestrates browser automation and GitHub CLI operations to perform sequential
  repository setup, PR analysis, and dependency installation tasks in an automated workflow.
version: 1.0.0
---

# Repo Analysis Pipeline

An automated data processing pipeline that performs sequential repository analysis and dependency management tasks. The pipeline consists of five stages that execute in a defined sequence, with data automatically flowing between stages. Upon completion, the pipeline can be configured to restart for continuous iteration.

## Usage

The pipeline executes automatically once initiated. Each stage processes its input and passes output to the next stage. Configuration can be adjusted through environment variables or pipeline parameters.

### Basic Execution
```bash
# Start the pipeline (implementation specific)
./repo-analysis-pipeline start

# Monitor pipeline status
./repo-analysis-pipeline status

# Stop the pipeline
./repo-analysis-pipeline stop
```

### Configuration
Set environment variables to customize pipeline behavior:
```bash
export PIPELINE_ITERATIONS=5      # Number of complete cycles
export GITHUB_TOKEN="your_token"  # GitHub authentication
export OUTPUT_FORMAT="json"       # Output format (json/text)
```

## Examples

### Example 1: Basic Pipeline Execution
```bash
# Execute a single iteration of the pipeline
./repo-analysis-pipeline --iterations 1 --output results.json
```

### Example 2: Continuous Monitoring Mode
```bash
# Run pipeline continuously with 60-second intervals
./repo-analysis-pipeline --continuous --interval 60 --log-level debug
```

### Example 3: Custom Repository Target
```bash
# Analyze specific repository with custom SHA
export TARGET_REPO="owner/repo-name"
export COMMIT_SHA="abc123def456"
./repo-analysis-pipeline --target $TARGET_REPO --sha $COMMIT_SHA
```

## Pipeline Stages

The pipeline consists of five sequential stages that execute in order. Each stage receives input from the previous stage and produces output for the next stage.

### Stage 1: Dependency Installation
- **Tool**: Browser automation
- **Command**: `npm install`
- **Description**: Installs project dependencies from package.json
- **Input**: Project configuration and package manifest
- **Output**: Installation result status (string)
- **Next Stage**: Flows to GitHub CLI (Stage 2)

### Stage 2: Pull Request Analysis
- **Tool**: GitHub CLI
- **Command**: `gh pr list --search "SHA_HERE" --state merged --json number,title,url`
- **Description**: Searches for merged pull requests containing a specific commit SHA
- **Input**: Commit SHA and repository context from previous stage
- **Output**: JSON array of PR data including numbers, titles, and URLs
- **Next Stage**: Flows to Browser (Stage 3)

### Stage 3: Global Command Setup
- **Tool**: Browser automation
- **Command**: `npm link`
- **Description**: Creates global command links for the installed package
- **Input**: Installation results from Stage 1
- **Output**: Link creation result status (string)
- **Next Stage**: Flows to GitHub CLI (Stage 4)

### Stage 4: Repository Star Analysis
- **Tool**: GitHub CLI
- **Command**: `gh api --paginate user/starred --jq '.[].full_name' | head -20`
- **Description**: Retrieves the user's starred repositories (top 20)
- **Input**: User authentication and API context
- **Output**: List of repository full names (JSON/text)
- **Next Stage**: Flows to Browser (Stage 5)

### Stage 5: Final Dependency Verification
- **Tool**: Browser automation
- **Command**: `npm install`
- **Description**: Verifies and completes dependency installation
- **Input**: Repository context and previous installation state
- **Output**: Final installation verification result (string)
- **Next Stage**: Pipeline completion (can restart for next iteration)

## Data Flow

The pipeline implements the following data flow pattern:
```
Stage 1 (Browser) → Stage 2 (GitHub CLI) → Stage 3 (Browser) → 
Stage 4 (GitHub CLI) → Stage 5 (Browser) → [Restart]
```

Each stage processes data and passes structured output to the next stage. The pipeline supports both JSON and text output formats, with error handling and retry logic at each stage boundary.

## Output Formats

The pipeline can produce output in multiple formats:

### JSON Output
```json
{
  "pipeline_run": {
    "id": "run_12345",
    "start_time": "2024-01-15T10:30:00Z",
    "duration_seconds": 45.2,
    "stages_completed": 5,
    "results": {
      "dependencies_installed": true,
      "prs_found": 3,
      "global_commands_linked": true,
      "starred_repos_analyzed": 20,
      "final_verification_passed": true
    }
  }
}
```

### Text Output
```
Pipeline Execution Complete
===========================
Run ID: run_12345
Duration: 45.2 seconds
Status: SUCCESS

Stage Results:
1. Dependency Installation: ✓ Success
2. PR Analysis: ✓ Found 3 merged PRs
3. Global Command Setup: ✓ Success
4. Star Analysis: ✓ Analyzed 20 repositories
5. Final Verification: ✓ Success
```

## Error Handling

The pipeline includes comprehensive error handling:
- **Stage Retry**: Failed stages automatically retry (up to 3 times)
- **Circuit Breaker**: Pipeline pauses if consecutive failures occur
- **Graceful Degradation**: Non-critical failures allow pipeline continuation
- **Detailed Logging**: All errors logged with context for debugging

## Performance Considerations

- Average execution time: 30-60 seconds per iteration
- Memory usage: ~100-200 MB per pipeline instance
- Network dependencies: Requires GitHub API access and npm registry
- Concurrent executions: Supports up to 5 parallel pipeline instances

---

*Note: This pipeline is designed for automated repository analysis and dependency management workflows. It requires appropriate permissions for GitHub API access and package installation.*
```