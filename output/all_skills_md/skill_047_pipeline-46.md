```yaml
---
name: repo-workflow-analyzer
description: A multi-stage automated data processing pipeline for GitHub repository workflow analysis and monitoring.
version: 1.0.0
---

# Repo Workflow Analyzer

An automated data processing pipeline designed to analyze GitHub repository workflows, track issues, pull requests, and monitor CI/CD run statuses. The pipeline operates through seven sequential stages, automatically processing and transforming data between each phase to provide comprehensive repository insights.

## Usage

The pipeline requires a configured GitHub CLI (`gh`) with appropriate authentication. The pipeline will automatically execute all stages in sequence, passing processed data between stages.

**Prerequisites:**
- GitHub CLI (`gh`) installed and authenticated
- Access to the target GitHub repository
- Sufficient API rate limits for the operations

**Basic Execution:**
```bash
# The pipeline will automatically start from Stage 1
./repo-workflow-analyzer --repo owner/repository-name
```

**With Custom Parameters:**
```bash
./repo-workflow-analyzer \
  --repo owner/repository-name \
  --pr-number 55 \
  --run-id 123456789 \
  --sha "abc123def456" \
  --output-format json
```

## Examples

### Example 1: Basic Repository Analysis
```bash
./repo-workflow-analyzer --repo octocat/Hello-World
```

**Expected Output Flow:**
1. Authenticates with GitHub
2. Lists all issues in the repository
3. Searches for merged PRs containing specific commits
4. Retrieves detailed PR information
5. Exports comprehensive issue data
6. Views CI/CD workflow run details
7. Re-authenticates for the next iteration cycle

### Example 2: Targeted PR Analysis
```bash
./repo-workflow-analyzer \
  --repo microsoft/vscode \
  --pr-number 142857 \
  --sha "fix123bug456" \
  --include-failed-runs
```

### Example 3: Batch Processing with JSON Output
```bash
./repo-workflow-analyzer \
  --repo facebook/react \
  --state all \
  --limit 500 \
  --output-format json \
  --output-file analysis-report.json
```

## Pipeline Stages

### Stage 1: Authentication Initialization
- **Tool:** GitHub CLI (`gh`)
- **Command:** `gh auth login`
- **Purpose:** Establishes authenticated session with GitHub API
- **Input:** Authentication credentials and configuration parameters
- **Output:** Authenticated session token and configuration files
- **Next Stage:** Automatically flows to Stage 2

### Stage 2: Issue Listing and Extraction
- **Tool:** GitHub CLI (`gh`)
- **Command:** `gh issue list --repo owner/repo --json number,title --jq '.[] | "\(.number): \(.title)"'`
- **Purpose:** Retrieves and formats repository issues for analysis
- **Input:** Repository specification and output formatting parameters
- **Output:** Formatted list of issues with numbers and titles
- **Next Stage:** Automatically flows to Stage 3

### Stage 3: Pull Request Search by Commit
- **Tool:** GitHub CLI (`gh`)
- **Command:** `gh pr list --search "SHA_HERE" --state merged --json number,title,url`
- **Purpose:** Identifies merged pull requests containing specific commit SHAs
- **Input:** Commit SHA and search parameters
- **Output:** JSON array of matching PRs with metadata
- **Next Stage:** Automatically flows to Stage 4

### Stage 4: Detailed PR Information Retrieval
- **Tool:** GitHub CLI (`gh`)
- **Command:** `gh api repos/owner/repo/pulls/55 --jq '.title, .state, .user.login'`
- **Purpose:** Fetches comprehensive details for specific pull requests
- **Input:** PR number and field selection parameters
- **Output:** Extracted PR metadata including title, state, and author
- **Next Stage:** Automatically flows to Stage 5

### Stage 5: Comprehensive Issue Data Export
- **Tool:** GitHub CLI (`gh`)
- **Command:** `gh issue list --state all --limit 9999 --json number,title,state,labels,assignees > issues.json`
- **Purpose:** Exports complete issue dataset for offline analysis
- **Input:** Repository specification and data scope parameters
- **Output:** JSON file containing all issue data with rich metadata
- **Next Stage:** Automatically flows to Stage 6

### Stage 6: Workflow Run Analysis
- **Tool:** GitHub CLI (`gh`)
- **Command:** `gh run view <run-id> --repo owner/repo --log-failed`
- **Purpose:** Examines CI/CD workflow execution details and failures
- **Input:** Workflow run identifier and repository context
- **Output:** Detailed run information including failure logs
- **Next Stage:** Automatically flows to Stage 7

### Stage 7: Session Renewal
- **Tool:** GitHub CLI (`gh`)
- **Command:** `gh auth login`
- **Purpose:** Refreshes authentication for continuous pipeline operation
- **Input:** Updated credentials or token refresh parameters
- **Output:** Renewed authentication session
- **Next Stage:** Returns to Stage 1 for next iteration cycle

## Data Flow Architecture

The pipeline implements a unidirectional data flow with the following characteristics:

1. **Sequential Processing:** Each stage completes before the next begins
2. **Data Transformation:** Output from each stage becomes input for the next
3. **State Persistence:** Authentication and configuration persist across stages
4. **Iterative Cycle:** Pipeline restarts automatically after Stage 7
5. **Error Handling:** Failed stages halt the pipeline with diagnostic output

## Configuration Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `--repo` | string | Target repository in owner/name format | Required |
| `--pr-number` | integer | Specific PR number for detailed analysis | None |
| `--run-id` | integer | Workflow run identifier for inspection | None |
| `--sha` | string | Commit SHA for PR search operations | None |
| `--state` | string | Issue/PR state filter (open, closed, all) | "all" |
| `--limit` | integer | Maximum records to retrieve per operation | 30 |
| `--output-format` | string | Output format (text, json, csv) | "text" |
| `--output-file` | string | File path for data export | "pipeline-output.json" |
| `--include-failed-runs` | flag | Include failed workflow runs in analysis | false |

## Output Formats

The pipeline supports multiple output formats:

1. **Text Format:** Human-readable console output
2. **JSON Format:** Structured data for programmatic consumption
3. **CSV Format:** Tabular data for spreadsheet applications
4. **File Export:** Persistent storage of complete datasets

## Error Handling

The pipeline includes comprehensive error handling:

- **Authentication Failures:** Prompt for credential renewal
- **API Rate Limits:** Automatic backoff and retry logic
- **Network Issues:** Exponential retry with increasing delays
- **Data Validation:** Input sanitization and format verification
- **Stage Failures:** Graceful degradation with error reporting

## Performance Considerations

1. **API Rate Limiting:** Implements intelligent request pacing
2. **Data Caching:** Local cache for repeated queries
3. **Parallel Processing:** Concurrent operations where supported
4. **Memory Management:** Stream processing for large datasets
5. **Network Optimization:** Connection pooling and reuse

## Security Notes

- All authentication tokens are handled securely
- No credentials are logged or stored in plaintext
- API requests use encrypted HTTPS connections
- Local cache files are permission-restricted
- Sensitive data is redacted from logs

---

*Note: This tool is designed for legitimate repository analysis and monitoring purposes. Ensure you have appropriate permissions before analyzing any repository.*
```