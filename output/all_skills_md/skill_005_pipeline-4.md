```yaml
---
name: web-repo-sync
description: |
  A multi-stage automated data processing pipeline that synchronizes web content
  with GitHub repository information. The pipeline orchestrates browser automation
  and GitHub CLI operations in a sequential workflow, with automatic stage
  transitions and iterative execution cycles.
version: 1.0.0
---

# Web Repository Synchronization Pipeline

The `web-repo-sync` pipeline is an automated data processing workflow that coordinates browser-based web interactions with GitHub repository operations. It executes seven sequential stages, passing output data between stages, and automatically restarts upon completion for continuous iteration.

## Usage

To execute the pipeline, invoke the main pipeline command. The pipeline will run through all stages automatically.

```bash
# Execute the complete pipeline
web-repo-sync
```

The pipeline accepts configuration through environment variables or a configuration file to customize target URLs and repository details.

### Configuration

Set the following environment variables before execution:

```bash
export TARGET_URL="https://example.com"
export GITHUB_REPO="owner/repo"
export PR_NUMBER="55"
```

## Examples

### Basic Execution

Run the pipeline with default settings:

```bash
web-repo-sync
```

### Custom Repository Target

Execute the pipeline targeting a specific repository:

```bash
export GITHUB_REPO="myorg/myrepo"
export PR_NUMBER="123"
web-repo-sync
```

### Pipeline Output

The pipeline produces structured output at each stage, which can be captured for analysis:

```bash
# Capture pipeline output to a file
web-repo-sync > pipeline_output.log
```

## Pipeline Stages

The pipeline consists of seven sequential stages that execute in order. Each stage's output becomes the input context for the subsequent stage.

### Stage 1: Initial Web Access
- **Tool**: `agent-browser`
- **Command**: `open https://example.com`
- **Input**: Web session parameters and URL
- **Output**: Web page content as string result
- **Next Stage**: Automatically transitions to GitHub Issue Listing

This stage initiates the browser session and loads the target webpage, establishing the initial data context for the pipeline.

### Stage 2: GitHub Issue Retrieval
- **Tool**: `github` (gh CLI)
- **Command**: `gh issue list --repo owner/repo --json number,title --jq '.[] | "\(.number): \(.title)"'`
- **Input**: Repository specification and output formatting options
- **Output**: Formatted list of repository issues
- **Next Stage**: Automatically transitions to Browser Dependency Setup

Retrieves and formats current issues from the specified GitHub repository, providing repository status context.

### Stage 3: Browser Environment Preparation
- **Tool**: `agent-browser`
- **Command**: `install --with-deps` (Linux: includes system dependencies)
- **Input**: Installation parameters and dependency flags
- **Output**: Installation status and environment details
- **Next Stage**: Automatically transitions to GitHub PR Details

Ensures the browser automation environment is fully configured with necessary dependencies for subsequent operations.

### Stage 4: Pull Request Analysis
- **Tool**: `github` (gh CLI)
- **Command**: `gh api repos/owner/repo/pulls/55 --jq '.title, .state, .user.login'`
- **Input**: API endpoint specification and data extraction query
- **Output**: Key pull request metadata (title, state, author)
- **Next Stage**: Automatically transitions to Browser Component Installation

Fetches detailed information about a specific pull request, extracting relevant metadata for processing.

### Stage 5: Browser Component Installation
- **Tool**: `agent-browser`
- **Command**: `install` (Chromium download)
- **Input**: Installation configuration parameters
- **Output**: Component installation status and version information
- **Next Stage**: Automatically transitions to PR Status Verification

Downloads and configures the browser automation component (Chromium) required for web interactions.

### Stage 6: PR Status Verification
- **Tool**: `github` (gh CLI)
- **Command**: `gh pr checks 55 --repo owner/repo`
- **Input**: PR identifier and repository specification
- **Output**: Status check results for the specified pull request
- **Next Stage**: Automatically transitions to Final Web Validation

Retrieves and reports the status of automated checks (CI/CD) for the target pull request.

### Stage 7: Final Web Validation
- **Tool**: `agent-browser`
- **Command**: `open https://example.com`
- **Input**: Web session parameters and validation URL
- **Output**: Final web content verification result
- **Next Stage**: Pipeline completion - automatically restarts for next iteration

Performs a final validation by accessing the target webpage, completing the synchronization cycle before the pipeline restarts.

## Data Flow

The pipeline implements a unidirectional data flow where each stage's `result` output is passed as contextual input to the subsequent stage. The pipeline maintains execution state throughout all seven stages, then resets and begins a new iteration automatically.

```
Stage 1 → Stage 2 → Stage 3 → Stage 4 → Stage 5 → Stage 6 → Stage 7 → (Restart)
```

## Notes

- The pipeline runs continuously until manually terminated
- Each stage must complete successfully before the next stage begins
- Configuration should be verified before execution to ensure correct target URLs and repository paths
- The pipeline is designed for automated data synchronization between web content and repository states

---

*This tool is intended for security research and authorized testing purposes only.*