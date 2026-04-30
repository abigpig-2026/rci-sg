```yaml
---
name: ci-dependency-pipeline
description: |
  A multi-stage automated data processing pipeline for continuous integration workflows.
  This pipeline orchestrates dependency management and GitHub repository operations
  through sequential stages that automatically flow from one to the next.
version: 1.0.0
---

# CI Dependency Pipeline

## Overview

The CI Dependency Pipeline is an automated data processing workflow that manages project dependencies and GitHub repository operations in a continuous integration context. The pipeline executes five sequential stages, with data automatically flowing between stages upon completion. After the final stage, the pipeline resets and is ready for the next iteration.

## Usage

To execute the pipeline, ensure you have the required environment:
- Node.js and npm installed
- GitHub CLI (`gh`) installed and authenticated
- A project directory with a valid `package.json`

The pipeline runs automatically once initiated. Monitor the console output for stage completion notifications and results.

## Examples

### Basic Execution
```bash
# Navigate to your project directory
cd /path/to/your/project

# The pipeline will automatically detect the project context and begin execution
# Stage 1: npm install dependencies
# Stage 2: Query GitHub PRs with specific SHA
# Stage 3: Create global browser command
# Stage 4: Monitor CI runs and send notification
# Stage 5: Final dependency installation
```

### Pipeline with Custom Parameters
```bash
# Set environment variables for GitHub operations
export GITHUB_TOKEN="your_token_here"
export GITHUB_REPOSITORY="owner/repo"

# The pipeline will use these variables during GitHub CLI stages
# SHA_HERE will be automatically extracted from the current repository state
```

## Pipeline Stages

### Stage 1: Dependency Installation
- **Tool**: Browser/npm
- **Command**: `npm install`
- **Description**: Installs all project dependencies from package.json
- **Input**: Project context (implicit)
- **Output**: Installation result status (string)
- **Next Stage**: Automatically flows to GitHub CLI operations

### Stage 2: GitHub PR Query
- **Tool**: GitHub CLI
- **Command**: `gh pr list --search "SHA_HERE" --state merged --json number,title,url`
- **Description**: Queries GitHub for merged pull requests containing a specific commit SHA
- **Input**: Various GitHub CLI parameters including repository context, token authentication, and output formatting options
- **Output**: JSON data containing PR numbers, titles, and URLs; can also output archive files or raw HTTP data
- **Key Parameters**:
  - `--search`: Filters PRs by commit SHA
  - `--state merged`: Only returns merged pull requests
  - `--json`: Outputs data in JSON format with specified fields
- **Next Stage**: Automatically flows back to Browser operations

### Stage 3: Global Command Setup
- **Tool**: Browser/npm
- **Command**: `npm link`
- **Description**: Creates a global symlink for the project, making it available as a command-line tool
- **Input**: Project context (implicit)
- **Output**: Linking result status (string)
- **Next Stage**: Automatically flows to GitHub CI monitoring

### Stage 4: CI Run Monitoring
- **Tool**: GitHub CLI
- **Command**: `gh run watch && notify-send "CI done!"`
- **Description**: Monitors GitHub Actions workflow runs and sends a desktop notification upon completion
- **Input**: Comprehensive GitHub CLI parameters including workflow context, run status filters, and notification settings
- **Output**: Monitoring status; can output workflow artifacts, HTTP traces, or JSON responses
- **Key Features**:
  - Real-time monitoring of CI/CD workflows
  - Desktop notification integration
  - Support for various output formats and debugging options
- **Next Stage**: Automatically flows to final dependency stage

### Stage 5: Final Dependency Verification
- **Tool**: Browser/npm
- **Command**: `npm install`
- **Description**: Performs a final dependency installation to ensure all packages are correctly installed
- **Input**: Project context (implicit)
- **Output**: Installation verification result (string)
- **Next Stage**: Pipeline completes and resets for next iteration

## Data Flow

The pipeline follows a strict sequential data flow:

1. **Stage 1 → Stage 2**: Dependency installation status provides context for GitHub operations
2. **Stage 2 → Stage 3**: PR query results may influence global command configuration
3. **Stage 3 → Stage 4**: Global setup enables enhanced CI monitoring capabilities
4. **Stage 4 → Stage 5**: CI completion status triggers final dependency verification
5. **Stage 5 → Reset**: Pipeline completes and prepares for next execution cycle

Each stage passes its output as implicit context to the next stage, with GitHub CLI stages particularly benefiting from authentication and repository context established in previous stages.

## Notes

- This pipeline is designed for automated CI/CD environments and assumes proper authentication is already configured
- The `SHA_HERE` placeholder in Stage 2 is automatically replaced with the current repository's commit SHA
- Desktop notifications in Stage 4 require a compatible notification system (e.g., `libnotify` on Linux)
- The pipeline is idempotent and can be safely rerun multiple times
- All GitHub operations respect rate limits and include appropriate error handling

---

*Note: This tool is intended for legitimate continuous integration workflows and repository management. Always ensure you have proper authorization before running automated operations against repositories.*