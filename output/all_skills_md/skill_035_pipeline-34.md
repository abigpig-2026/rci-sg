```yaml
---
name: repo-analysis-pipeline
description: A multi-stage automated data processing pipeline for repository analysis and dependency management. The pipeline orchestrates browser automation and GitHub CLI operations to collect repository metadata and manage project dependencies in a continuous cycle.
version: 1.0.0
---

# Repo Analysis Pipeline

The Repo Analysis Pipeline is an automated data processing workflow designed to streamline repository analysis and dependency management tasks. It operates through five distinct stages, automatically passing data and control between browser automation and GitHub CLI operations. Upon completion of all stages, the pipeline resets and begins a new iteration for continuous optimization.

## Usage

To execute the pipeline, ensure you have the necessary environment configured:
- Node.js and npm installed
- GitHub CLI (`gh`) installed and authenticated
- A modern web browser available for automation

The pipeline runs autonomously once initiated. You can monitor its progress through the output of each stage.

### Basic Execution
```bash
# The pipeline is typically invoked by a controller script or orchestration tool
./run-pipeline.sh
```

### Configuration
Set the following environment variables to customize pipeline behavior:
- `GITHUB_TOKEN`: Your GitHub Personal Access Token (for `gh` CLI)
- `NODE_ENV`: Node.js environment (default: `production`)
- `PIPELINE_ITERATIONS`: Number of pipeline cycles to run (default: infinite)

## Examples

### Example 1: Standard Pipeline Execution
```bash
# Set up environment
export GITHUB_TOKEN="ghp_your_token_here"
export NODE_ENV="development"

# Run pipeline with logging
./repo-analysis-pipeline --log-level=verbose --max-iterations=5
```

### Example 2: Pipeline with Custom SHA Search
```bash
# Execute pipeline searching for specific commit SHA
export SEARCH_SHA="a1b2c3d4e5f67890"
./repo-analysis-pipeline --search-sha=$SEARCH_SHA
```

### Example 3: Pipeline Output to File
```bash
# Redirect pipeline output to log file
./repo-analysis-pipeline > pipeline-output.log 2>&1 &
```

## Pipeline Stages

The pipeline consists of five sequential stages that execute in order. Each stage completes its task and automatically triggers the next stage.

### Stage 1: Dependency Installation
- **Tool**: Browser Automation
- **Command**: `npm install`
- **Description**: Installs project dependencies by simulating browser-based npm package installation. This stage prepares the environment for subsequent repository analysis tasks.
- **Input**: Configuration parameters (environment-specific)
- **Output**: Installation result status as string
- **Next Stage**: Automatically proceeds to Stage 2 (GitHub CLI)

### Stage 2: Pull Request Analysis
- **Tool**: GitHub CLI
- **Command**: `gh pr list --search "SHA_HERE" --state merged --json number,title,url`
- **Description**: Queries GitHub for merged pull requests containing a specific commit SHA. The search parameter `SHA_HERE` is dynamically populated from pipeline context or previous stage output.
- **Input**: GitHub CLI parameters including repository context, authentication tokens, and search filters
- **Output**: JSON data containing PR numbers, titles, and URLs; may also output archive files or HTTP logs
- **Next Stage**: Automatically proceeds to Stage 3 (Browser)

### Stage 3: Global Command Setup
- **Tool**: Browser Automation
- **Command**: `npm link`
- **Description**: Creates a global 'browser' command by linking the npm package. This enables subsequent stages to invoke browser automation tools system-wide.
- **Input**: Package configuration parameters
- **Output**: Linking result status as string
- **Next Stage**: Automatically proceeds to Stage 4 (GitHub CLI)

### Stage 4: Repository Metadata Collection
- **Tool**: GitHub CLI
- **Command**: `gh api --paginate user/starred --jq '.[].full_name' | head -20`
- **Description**: Fetches the user's starred repositories from GitHub API, paginates through results, extracts full repository names using jq, and returns the first 20 entries.
- **Input**: GitHub API parameters including pagination settings, output formatting, and authentication
- **Output**: List of repository names (first 20); may include JSON responses or archive files
- **Next Stage**: Automatically proceeds to Stage 5 (Browser)

### Stage 5: Final Dependency Verification
- **Tool**: Browser Automation
- **Command**: `npm install`
- **Description**: Performs a final dependency installation to verify environment consistency and ensure all required packages are properly installed for the next pipeline iteration.
- **Input**: Dependency specifications and environment parameters
- **Output**: Installation verification result as string
- **Next Stage**: Pipeline completes cycle and returns to Stage 1 for next iteration

## Data Flow

The pipeline maintains state through the following data flow pattern:

1. **Stage 1 → Stage 2**: Installation status informs GitHub CLI authentication and context
2. **Stage 2 → Stage 3**: PR analysis results may influence global command configuration
3. **Stage 3 → Stage 4**: Global setup enables enhanced GitHub API access
4. **Stage 4 → Stage 5**: Repository metadata guides final dependency resolution
5. **Stage 5 → Stage 1**: Verification results feed into next iteration's initial setup

Each stage consumes the output of the previous stage as contextual input, creating a continuous data processing loop.

## Iteration Cycle

After Stage 5 completes, the pipeline automatically resets and begins a new iteration at Stage 1. This continuous cycle allows for:
- Progressive optimization of dependency management
- Ongoing monitoring of repository changes
- Adaptive configuration based on previous results
- Cumulative data collection across multiple cycles

The pipeline runs indefinitely until manually stopped or until a predefined iteration limit is reached.

---

*Note: This tool is designed for legitimate repository analysis and dependency management purposes. Always ensure you have proper authorization before analyzing repositories or accessing GitHub data.*