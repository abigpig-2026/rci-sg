---
name: repo-analysis-pipeline
description: A multi-stage automated data processing pipeline for repository analysis and dependency management
version: 1.0.0
---

# Repo Analysis Pipeline

An automated data processing pipeline that performs repository analysis through sequential stages. The pipeline orchestrates browser-based operations and GitHub CLI commands to analyze repository data, manage dependencies, and extract insights. Each stage processes data and automatically passes results to the next stage, creating a continuous optimization loop.

## Usage

To execute the pipeline, run the main orchestration script:

```bash
./run-pipeline.sh [OPTIONS]
```

### Options

- `--repo-url`: Target repository URL (optional)
- `--sha`: Specific commit SHA to analyze (optional)
- `--output-dir`: Directory for pipeline outputs (default: ./output)
- `--iterations`: Number of pipeline iterations (default: 1)

### Environment Variables

```bash
export GITHUB_TOKEN=your_github_token
export NODE_ENV=production
```

## Examples

### Basic Repository Analysis

```bash
# Analyze a specific repository
./run-pipeline.sh --repo-url https://github.com/example/repo

# Analyze with a specific commit SHA
./run-pipeline.sh --repo-url https://github.com/example/repo --sha abc123def456

# Run multiple iterations for continuous optimization
./run-pipeline.sh --repo-url https://github.com/example/repo --iterations 3
```

### Integration with CI/CD

```yaml
# GitHub Actions example
name: Repository Analysis Pipeline
on: [push]
jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Analysis Pipeline
        run: |
          chmod +x run-pipeline.sh
          ./run-pipeline.sh --repo-url ${{ github.repositoryUrl }} --sha ${{ github.sha }}
```

## Pipeline Stages

The pipeline consists of 5 sequential stages that execute in order. After the final stage completes, the pipeline can restart for additional iterations based on configuration.

### Stage 1: Dependency Installation
- **Tool**: Browser automation
- **Command**: `npm install`
- **Description**: Installs project dependencies from package.json
- **Input**: Repository context and configuration
- **Output**: Installation result status (string)
- **Next Stage**: github-cli (Stage 2)

This stage prepares the environment by installing all required dependencies for the repository analysis.

### Stage 2: Pull Request Analysis
- **Tool**: GitHub CLI
- **Command**: `gh pr list --search "SHA_HERE" --state merged --json number,title,url`
- **Description**: Searches for merged pull requests containing a specific commit SHA
- **Input**: Various GitHub CLI parameters including JSON output format, search filters, and repository context
- **Output**: JSON data containing PR information, optionally formatted or processed
- **Next Stage**: browser (Stage 3)

Analyzes the repository's pull request history to identify merged changes related to specific commits.

### Stage 3: Global Command Setup
- **Tool**: Browser automation
- **Command**: `npm link`
- **Description**: Creates a global 'browser' command for system-wide access
- **Input**: Installation context
- **Output**: Link creation result status (string)
- **Next Stage**: github-cli (Stage 4)

Sets up global access to browser automation tools for subsequent pipeline operations.

### Stage 4: Repository Star Analysis
- **Tool**: GitHub CLI
- **Command**: `gh api --paginate user/starred --jq '.[].full_name' | head -20`
- **Description**: Retrieves the user's starred repositories and extracts the first 20 repository names
- **Input**: Extensive GitHub CLI parameters including pagination, JSON query, and API options
- **Output**: Processed repository data in various formats (JSON, files, URLs)
- **Next Stage**: browser (Stage 5)

Collects data about starred repositories to understand user preferences and popular projects.

### Stage 5: Final Dependency Verification
- **Tool**: Browser automation
- **Command**: `npm install`
- **Description**: Verifies and reinstalls dependencies to ensure consistency
- **Input**: Pipeline context
- **Output**: Installation verification result (string)
- **Next Stage**: Returns to Stage 1 for next iteration (if configured)

Performs a final dependency check to ensure all components are properly installed before pipeline completion or next iteration.

## Data Flow

The pipeline follows a strict sequential data flow:

1. **Stage 1 → Stage 2**: Installation status → PR search parameters
2. **Stage 2 → Stage 3**: PR analysis results → Global tool setup
3. **Stage 3 → Stage 4**: Setup completion → Repository data collection
4. **Stage 4 → Stage 5**: Starred repository data → Final verification
5. **Stage 5 → Stage 1**: Verification results → Next iteration (if configured)

Each stage processes the output from the previous stage and prepares data for the next stage. The pipeline supports configurable iterations for continuous optimization.

## Output Formats

The pipeline produces multiple output types:

- **JSON**: Structured data from GitHub API responses
- **Files**: Archived data and configuration files
- **Strings**: Status messages and command results
- **URLs**: References to external resources and API endpoints

All outputs are stored in the specified output directory with timestamp-based organization.

## Error Handling

The pipeline includes comprehensive error handling:

- **Stage failures**: Individual stage failures trigger retry logic
- **Data validation**: Each stage validates input data before processing
- **Graceful degradation**: Partial results are preserved when possible
- **Logging**: Detailed logs are maintained for debugging and audit purposes

## Security Considerations

This pipeline requires appropriate authentication and should only be used with authorized repositories. Ensure that:

1. GitHub tokens have minimal required permissions
2. Repository access is properly authorized
3. Output data is stored securely
4. Pipeline execution is monitored and logged

---

*Note: This pipeline is designed for legitimate repository analysis and dependency management tasks. Always ensure compliance with repository terms of service and applicable laws.*