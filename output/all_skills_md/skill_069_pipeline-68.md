---
name: website-deploy-pipeline
description: A multi-stage automated pipeline for website deployment and optimization with GitHub integration
version: 1.0.0
---

# Website Deploy Pipeline

An automated, multi-stage data processing pipeline designed to streamline website deployment and optimization workflows. The pipeline orchestrates authentication, repository management, image optimization, and deployment tasks in a sequential, automated fashion. Upon completion of all stages, the pipeline automatically restarts for continuous iteration and optimization.

## Usage

The pipeline is executed as a single command. It requires a configuration file or environment variables to specify target repositories and deployment parameters.

```bash
# Basic execution
run-pipeline --config deploy-config.yaml

# With environment overrides
GITHUB_TOKEN=your_token REPO_NAME=my-website run-pipeline
```

### Prerequisites

- GitHub CLI (`gh`) installed and configured
- Node.js and npm for Squoosh CLI
- Git installed and configured
- Valid GitHub authentication token with appropriate repository permissions

### Configuration

Create a `deploy-config.yaml` file:

```yaml
target_repository: "username/website-repo"
source_directory: "./website"
image_optimization:
  format: "webp"
  quality: "auto"
deployment_branch: "gh-pages"
notification_enabled: true
```

## Examples

### Example 1: Full Website Deployment

```bash
# Configure environment
export GITHUB_TOKEN="ghp_xxxxxxxxxxxx"
export TARGET_REPO="myorg/mysite"

# Run the pipeline
run-pipeline --repo $TARGET_REPO --source ./dist --optimize-images
```

### Example 2: Incremental Update with Specific Commit

```bash
# Deploy only changed files with a specific commit message
run-pipeline \
  --repo "user/project" \
  --commit-sha "abc123def456" \
  --message "Update documentation" \
  --incremental
```

### Example 3: Dry Run for Testing

```bash
# Test the pipeline without making actual changes
run-pipeline \
  --config test-config.yaml \
  --dry-run \
  --verbose
```

## Pipeline Stages

The pipeline consists of 7 sequential stages that execute in order, with automatic data flow between stages.

### Stage 1: Authentication Initialization
- **Tool**: GitHub CLI (`gh`)
- **Command**: `gh auth login`
- **Purpose**: Establishes authenticated session with GitHub API
- **Input**: Authentication tokens, hostname configuration, scope permissions
- **Output**: Authenticated session, configuration files
- **Next Stage**: Stage 2 (Image Optimization)

### Stage 2: Image Optimization
- **Tool**: Squoosh CLI
- **Command**: `npx squoosh-cli website/images/*.jpg --webp auto`
- **Purpose**: Compresses and converts website images to WebP format
- **Input**: JPEG images from website directory, optimization parameters
- **Output**: Optimized WebP images, compression statistics
- **Next Stage**: Stage 3 (PR Analysis)

### Stage 3: Pull Request Analysis
- **Tool**: GitHub CLI (`gh`)
- **Command**: `gh pr list --search "SHA_HERE" --state merged --json number,title,url`
- **Purpose**: Analyzes merged pull requests related to the deployment
- **Input**: Commit SHA, repository context, state filters
- **Output**: JSON data of relevant PRs, metadata for deployment tracking
- **Next Stage**: Stage 4 (Repository Update)

### Stage 4: Repository Synchronization
- **Tool**: Git
- **Command**: `git push`
- **Purpose**: Pushes optimized content to the remote repository
- **Input**: Committed changes, remote repository URL, branch information
- **Output**: Synchronized repository, push confirmation
- **Next Stage**: Stage 5 (CI Monitoring)

### Stage 5: Continuous Integration Monitoring
- **Tool**: GitHub CLI (`gh`) with system notification
- **Command**: `gh run watch && notify-send "CI done!"`
- **Purpose**: Monitors GitHub Actions workflows and notifies upon completion
- **Input**: Workflow run ID, repository context
- **Output**: Workflow status, desktop notification
- **Next Stage**: Stage 6 (Commit Finalization)

### Stage 6: Commit Finalization
- **Tool**: Git
- **Command**: `git commit -m "Add website"`
- **Purpose**: Creates final commit with deployment changes
- **Input**: Staged changes, commit message template
- **Output**: Commit hash, commit confirmation
- **Next Stage**: Stage 7 (Session Renewal)

### Stage 7: Session Renewal
- **Tool**: GitHub CLI (`gh`)
- **Command**: `gh auth login`
- **Purpose**: Renews authentication session for next pipeline iteration
- **Input**: Updated tokens, session refresh parameters
- **Output**: Renewed session, updated credentials
- **Next Stage**: Stage 1 (Restart pipeline)

## Data Flow

The pipeline maintains state through the following data flow:

1. **Authentication tokens** persist through all GitHub CLI stages
2. **Optimized image files** flow from Stage 2 to Stage 4 for deployment
3. **Commit metadata** flows from Stage 3 to Stage 6 for contextual commits
4. **Repository state** is maintained throughout all Git operations
5. **Session information** cycles from Stage 7 back to Stage 1

## Error Handling

The pipeline includes built-in error handling:

- **Authentication failures**: Retry with exponential backoff
- **Network issues**: Automatic retry for up to 3 attempts
- **Image processing errors**: Skip problematic files with logging
- **Git conflicts**: Attempt automatic merge, fall back to manual resolution prompt

## Output

Successful pipeline execution produces:

1. Deployed website to specified GitHub Pages branch
2. Optimized image assets in WebP format
3. Detailed log file with timing and performance metrics
4. JSON report of all actions performed
5. Notification of completion (if enabled)

## Notes

- This pipeline is designed for automated deployment scenarios
- All GitHub operations respect rate limits and implement appropriate delays
- Image optimization preserves original files as backups
- The pipeline creates automatic rollback points before destructive operations