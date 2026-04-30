---
name: ci-dependency-pipeline
description: A multi-stage automated data processing pipeline for CI/CD dependency management and GitHub repository monitoring
version: 1.0.0
---

# CI Dependency Pipeline

An automated data processing pipeline that orchestrates dependency installation, GitHub repository monitoring, and CI/CD workflow management. The pipeline consists of five sequential stages that execute in a continuous loop, with each stage's output automatically flowing to the next stage for further processing.

## Usage

To execute the complete pipeline:

```bash
# Start the pipeline with initial parameters
pipeline-run --start-stage browser --input-params "project_path=/path/to/project"
```

The pipeline will automatically progress through all stages and restart for the next iteration upon completion.

## Examples

### Basic Pipeline Execution
```bash
# Run the complete pipeline cycle
pipeline-run --full-cycle --monitor-output

# Execute specific stage with custom parameters
pipeline-run --stage github-cli --param "search_query=SHA_HERE" --param "state=merged"
```

### Pipeline Configuration
```yaml
# pipeline-config.yaml
pipeline:
  name: ci-dependency-pipeline
  stages:
    - browser: "npm install"
    - github-cli: "gh pr list --search 'SHA_HERE' --state merged --json number,title,url"
    - browser: "npm link"
    - github-cli: "gh run watch && notify-send 'CI done!'"
    - browser: "npm install"
  
  iteration_delay: 300  # seconds between iterations
  max_iterations: 10    # maximum pipeline cycles
```

## Pipeline Stages

### Stage 1: Dependency Installation (Browser)
- **Description**: Installs project dependencies using npm package manager
- **Command**: `npm install`
- **Input**: Configuration parameters for dependency resolution
- **Output**: Installation result status as string
- **Next Stage**: Automatically flows to GitHub CLI stage

### Stage 2: GitHub PR Monitoring (GitHub CLI)
- **Description**: Queries GitHub for merged pull requests containing specific commit SHA
- **Command**: `gh pr list --search "SHA_HERE" --state merged --json number,title,url`
- **Input**: GitHub repository context and search parameters
- **Output**: JSON-formatted pull request data including PR numbers, titles, and URLs
- **Next Stage**: Automatically flows to Browser stage for command linking

### Stage 3: Command Linking (Browser)
- **Description**: Creates global command links for installed packages
- **Command**: `npm link`
- **Input**: Previous stage output and package configuration
- **Output**: Linking result status as string
- **Next Stage**: Automatically flows to GitHub CLI stage for CI monitoring

### Stage 4: CI Workflow Monitoring (GitHub CLI)
- **Description**: Monitors GitHub Actions runs and sends notification upon completion
- **Command**: `gh run watch && notify-send "CI done!"`
- **Input**: Repository workflow context and monitoring parameters
- **Output**: Workflow status data and notification confirmation
- **Next Stage**: Automatically flows to final Browser stage

### Stage 5: Final Dependency Verification (Browser)
- **Description**: Verifies and reinstalls dependencies to ensure consistency
- **Command**: `npm install`
- **Input**: Verification parameters and previous stage context
- **Output**: Final installation verification result as string
- **Next Stage**: Pipeline restarts from Stage 1 for next iteration

## Data Flow

The pipeline implements a continuous data processing flow:

```
Stage 1 (Browser) → Stage 2 (GitHub CLI) → Stage 3 (Browser) → Stage 4 (GitHub CLI) → Stage 5 (Browser) → [Restart]
```

Each stage processes input from the previous stage and produces output for the next stage. The pipeline maintains state between iterations, allowing for incremental optimization of dependency management and repository monitoring tasks.

## Configuration Parameters

### Browser Stage Parameters
- `project_path`: Path to the project directory
- `dependency_file`: Custom package.json file location
- `install_flags`: Additional npm install flags

### GitHub CLI Stage Parameters
- `repository`: Target GitHub repository (owner/repo format)
- `search_query`: Commit SHA or search pattern for PR filtering
- `output_format`: JSON output structure customization
- `notification_method`: Desktop notification configuration

## Output Formats

The pipeline produces structured output at each stage:

1. **String Results**: Installation and linking status messages
2. **JSON Data**: GitHub PR information with number, title, and URL fields
3. **File Outputs**: Archived data and configuration files
4. **Notification Events**: System notifications for CI completion

## Error Handling

The pipeline includes built-in error recovery mechanisms:
- Stage failure triggers automatic retry with exponential backoff
- Invalid output from one stage is filtered before passing to next stage
- Configuration validation occurs at pipeline initialization
- Critical errors pause the pipeline for manual intervention

## Security Considerations

This pipeline requires appropriate permissions:
- GitHub personal access token with repo scope
- Local system permissions for npm operations
- Desktop notification permissions (if enabled)

All sensitive data is handled according to security best practices, with tokens and credentials managed through secure environment variables.

---

*Note: This pipeline is designed for automated CI/CD workflow management and repository monitoring. Ensure compliance with GitHub API rate limits and repository access policies when deploying in production environments.*