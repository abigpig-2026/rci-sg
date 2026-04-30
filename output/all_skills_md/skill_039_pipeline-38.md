---
name: repo-analysis-pipeline
description: A multi-stage automated data processing pipeline for repository analysis and dependency management. The pipeline orchestrates browser automation and GitHub CLI operations to collect repository metrics and prepare development environments.
version: 1.0.0
---

# Repo Analysis Pipeline

An automated data processing pipeline that performs repository analysis through sequential stages. The pipeline coordinates between browser automation for dependency management and GitHub CLI operations for repository data extraction, creating a continuous workflow for repository intelligence gathering.

## Usage

The pipeline runs automatically once initiated. It processes data through five sequential stages, with outputs from each stage serving as inputs or triggers for the next. The pipeline will restart upon completion for continuous monitoring.

**Basic invocation:**
```bash
# Start the pipeline
start-pipeline --target-repo <owner/repo>
```

**Configuration options:**
- `--target-repo`: Repository to analyze (format: owner/repo)
- `--sha`: Specific commit SHA to search for in PRs (optional)
- `--contributor-limit`: Number of contributors to display (default: 10)
- `--output-format`: Output format (json, text, csv)

## Examples

**Example 1: Analyze a specific repository**
```bash
start-pipeline --target-repo octocat/Hello-World --output-format json
```

**Example 2: Search for PRs containing a specific commit**
```bash
start-pipeline --target-repo microsoft/vscode --sha abc123def456 --contributor-limit 5
```

**Example 3: Continuous monitoring mode**
```bash
start-pipeline --target-repo facebook/react --interval 3600
# Runs pipeline every hour for continuous updates
```

## Pipeline Stages

### Stage 1: Dependency Installation
- **Tool**: Browser automation
- **Command**: `npm install`
- **Description**: Installs project dependencies by simulating browser-based package management operations. This stage prepares the environment for subsequent analysis tasks.
- **Input**: Environment configuration and package.json data
- **Output**: Installation status and dependency tree
- **Next Stage**: GitHub CLI PR search

### Stage 2: Pull Request Analysis
- **Tool**: GitHub CLI
- **Command**: `gh pr list --search "SHA_HERE" --state merged --json number,title,url`
- **Description**: Searches for merged pull requests containing a specific commit SHA. Extracts PR metadata including number, title, and URL for further analysis.
- **Input**: Commit SHA from repository history
- **Output**: JSON array of PR data with fields: number, title, url
- **Supported Parameters**: Extensive GitHub CLI options including search filters, state filters, JSON output formatting, and pagination controls
- **Next Stage**: Global command setup

### Stage 3: Global Command Configuration
- **Tool**: Browser automation
- **Command**: `npm link`
- **Description**: Creates global command links for the installed packages, enabling system-wide access to development tools required for repository analysis.
- **Input**: Successfully installed npm packages
- **Output**: Global command availability status
- **Next Stage**: Contributor analysis

### Stage 4: Contributor Statistics
- **Tool**: GitHub CLI
- **Command**: `gh api --paginate repos/owner/repo/contributors --jq '.[] | "\(.login): \(.contributions)"' | head -n`
- **Description**: Retrieves contributor statistics from the target repository using GitHub's REST API. Processes the data with jq to extract login names and contribution counts, limiting output to the top contributors.
- **Input**: Repository owner and name
- **Output**: Formatted list of contributors and their contribution counts
- **Supported Parameters**: Full GitHub CLI API options including pagination, filtering, JSON processing with jq, and output formatting
- **Next Stage**: Final dependency verification

### Stage 5: Final Dependency Verification
- **Tool**: Browser automation
- **Command**: `npm install`
- **Description**: Performs a final dependency verification to ensure all packages are correctly installed and available. This stage completes the environment setup cycle and prepares for the next pipeline iteration.
- **Input**: Package configuration from previous stages
- **Output**: Final installation verification status
- **Next Stage**: Pipeline restart for continuous operation

## Data Flow

The pipeline implements a unidirectional data flow where each stage's output informs the next stage's operation:

1. **Stage 1 → Stage 2**: Dependency installation enables GitHub CLI operations
2. **Stage 2 → Stage 3**: PR analysis results inform global tool configuration
3. **Stage 3 → Stage 4**: Global commands enable API access for contributor data
4. **Stage 4 → Stage 5**: Contributor statistics guide final dependency verification
5. **Stage 5 → Stage 1**: Pipeline restarts with updated environment for continuous analysis

## Output Formats

The pipeline supports multiple output formats:

- **JSON**: Structured data for programmatic consumption
- **Text**: Human-readable formatted output
- **CSV**: Tabular data for spreadsheet applications
- **Raw**: Unprocessed API responses for custom parsing

## Error Handling

The pipeline includes robust error handling with:
- Automatic retry for failed stages
- Graceful degradation when optional data is unavailable
- Detailed logging for troubleshooting
- Checkpoint recovery for interrupted operations

## Security Notes

This pipeline requires appropriate authentication tokens for GitHub API access. Ensure tokens have minimal required permissions and are stored securely. The pipeline is designed for authorized repository analysis and should only be used on repositories you have permission to access.