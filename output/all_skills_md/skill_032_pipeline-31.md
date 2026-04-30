---
name: ci-dependency-pipeline
description: A multi-stage automated data processing pipeline for CI/CD dependency management and GitHub repository monitoring
version: 1.0.0
---

# CI Dependency Pipeline

An automated data processing pipeline that orchestrates dependency management and GitHub repository monitoring tasks. The pipeline consists of five sequential stages that execute in a continuous loop, automatically passing data between stages to complete a full iteration of CI/CD preparation and monitoring.

## Usage

To execute the pipeline, initiate the first stage. The pipeline will automatically progress through each stage, with outputs from one stage serving as inputs or triggers for the next.

```bash
# Start the pipeline (initiates Stage 1)
npm install
```

The pipeline will execute the following sequence:
1. Stage 1: Dependency installation
2. Stage 2: GitHub PR query and analysis
3. Stage 3: Global command setup
4. Stage 4: CI workflow monitoring
5. Stage 5: Dependency verification

After Stage 5 completes, the pipeline automatically restarts from Stage 1 for the next iteration cycle.

## Examples

### Basic Pipeline Execution
```bash
# Navigate to your project directory
cd /path/to/project

# Initialize the pipeline (triggers Stage 1)
npm install

# The pipeline automatically progresses through:
# 1. Installs dependencies (Stage 1)
# 2. Queries merged PRs with specific SHA (Stage 2)
# 3. Creates global browser command (Stage 3)
# 4. Monitors CI runs and sends notification (Stage 4)
# 5. Verifies dependencies (Stage 5)
# 6. Restarts pipeline for next iteration
```

### Pipeline with Custom SHA Search
```bash
# Set environment variable for PR search
export SEARCH_SHA="abc123def456"

# Start pipeline
npm install

# Stage 2 will execute: gh pr list --search "abc123def456" --state merged --json number,title,url
```

### Monitoring Specific Repository
```bash
# Configure GitHub CLI for target repository
gh repo set-default owner/repo-name

# Execute pipeline
npm install

# Pipeline will monitor CI runs for the specified repository in Stage 4
```

## Pipeline Stages

### Stage 1: Dependency Installation
- **Description**: Installs project dependencies using npm
- **Command**: `npm install`
- **Input**: None (initial stage trigger)
- **Output**: Installation result status (string)
- **Next Stage**: Automatically flows to Stage 2 (GitHub CLI)

### Stage 2: GitHub PR Analysis
- **Description**: Queries GitHub for merged pull requests containing a specific SHA
- **Command**: `gh pr list --search "SHA_HERE" --state merged --json number,title,url`
- **Input**: Receives trigger from Stage 1 completion
- **Output**: JSON data containing PR numbers, titles, and URLs; may include tar.gz archives or HTTP request/response details
- **Key Parameters**: 
  - `--search`: SHA to search for in PR commits
  - `--state merged`: Filters to only merged PRs
  - `--json`: Output format specification
- **Next Stage**: Automatically flows to Stage 3 (Browser)

### Stage 3: Global Command Setup
- **Description**: Creates a global command link for browser automation
- **Command**: `npm link`
- **Input**: Receives data from Stage 2 completion
- **Output**: Link creation result status (string)
- **Next Stage**: Automatically flows to Stage 4 (GitHub CLI)

### Stage 4: CI Workflow Monitoring
- **Description**: Monitors GitHub Actions workflow runs and sends system notification upon completion
- **Command**: `gh run watch && notify-send "CI done!"`
- **Input**: Receives trigger from Stage 3 completion
- **Output**: Monitoring status; may include workflow archives or JSON responses
- **Functionality**:
  - `gh run watch`: Continuously monitors CI workflow execution
  - `notify-send`: Sends desktop notification when CI completes
- **Next Stage**: Automatically flows to Stage 5 (Browser)

### Stage 5: Dependency Verification
- **Description**: Verifies and reinstalls dependencies to ensure consistency
- **Command**: `npm install`
- **Input**: Receives data from Stage 4 completion
- **Output**: Verification result status (string)
- **Next Stage**: Automatically restarts pipeline at Stage 1 for next iteration

## Data Flow

The pipeline implements a unidirectional data flow with automatic stage progression:

```
Stage 1 (npm install)
    ↓
Stage 2 (gh pr list --search "SHA")
    ↓
Stage 3 (npm link)
    ↓
Stage 4 (gh run watch && notify-send)
    ↓
Stage 5 (npm install)
    ↓
[Pipeline Restart] → Stage 1
```

Each stage completion automatically triggers the next stage execution. The pipeline is designed for continuous operation, making it suitable for ongoing CI/CD monitoring and dependency management workflows.

## Configuration Notes

- Ensure GitHub CLI (`gh`) is authenticated before pipeline execution
- The `notify-send` command in Stage 4 requires a desktop notification system (Linux)
- SHA search in Stage 2 can be customized via environment variables or pipeline configuration
- The pipeline assumes a Node.js/npm project structure for dependency management stages

## Iteration Behavior

After completing all five stages, the pipeline automatically restarts from Stage 1. This continuous iteration allows for:
- Regular dependency updates and verification
- Ongoing monitoring of GitHub PRs and CI workflows
- Automated response to repository changes
- Consistent environment state maintenance

Each iteration represents a complete cycle of dependency management and repository monitoring, making the pipeline suitable for integration into larger DevOps automation systems.