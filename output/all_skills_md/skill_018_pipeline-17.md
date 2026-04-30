```yaml
---
name: browser-automation-pipeline
description: A multi-stage automated data processing pipeline for browser automation and web content extraction.
version: 1.0.0
---

# Browser Automation Pipeline

This skill implements an automated, multi-stage data processing pipeline designed for browser automation tasks. The pipeline orchestrates a sequence of `agent-browser` operations, where the output of one stage automatically flows as input to the next. Upon completion of the final stage, the pipeline can be configured to restart for continuous or iterative processing cycles.

## Usage

The pipeline is invoked as a single skill. It accepts an initial configuration or trigger, and then manages the sequential execution of all defined stages internally.

**Basic Invocation:**
```bash
invoke browser-automation-pipeline
```

**With Initial Parameters (if supported by the runtime environment):**
```bash
invoke browser-automation-pipeline --param "initial_url=https://example.com"
```

The pipeline handles all inter-stage data passing automatically. Each stage receives the `result` string from the previous stage as part of its execution context.

## Examples

### Example 1: Standard Execution
Execute the full pipeline from start to finish.
```bash
$ invoke browser-automation-pipeline
[INFO] Starting Browser Automation Pipeline v1.0.0
[INFO] Stage 1: Opening initial URL...
[INFO] Stage 1 Complete. Result: <Page loaded>
[INFO] Stage 2: Installing with dependencies...
...
[INFO] Pipeline cycle complete. Ready for next iteration.
```

### Example 2: Integration in a Larger Workflow
This pipeline can be used as a component within a larger data-gathering or monitoring system, where its JSON output from Stage 6 is parsed by a subsequent process.
```bash
# In a script or another skill
PIPELINE_OUTPUT=$(invoke browser-automation-pipeline --quiet)
EXTRACTED_DATA=$(echo $PIPELINE_OUTPUT | jq -r '.snapshot_data')
# Process $EXTRACTED_DATA further...
```

## Pipeline Stages

The pipeline consists of seven sequential stages, each performed by an `agent-browser` component.

### Stage 1: Initial Page Load
- **Description:** Opens the initial target URL (`https://example.com`) to establish a browser session and load primary content.
- **Input:** Accepts a URL parameter. In the first run, this is the configured starting point.
- **Output:** A `result` string containing status information (e.g., page load success, title, or initial DOM state).
- **Next Stage:** Output flows to Stage 2.

### Stage 2 & 3: System Dependency Installation
- **Description:** These stages handle the installation of necessary software dependencies, including system-level packages. The `--with-deps` flag indicates a comprehensive installation routine typical for Linux environments.
- **Input:** The `result` string from the previous stage.
- **Output:** A `result` string with installation logs and success/failure status.
- **Next Stage:** Stage 2 flows to Stage 3, then to Stage 4.

### Stage 4 & 5: Browser Engine Download
- **Description:** These stages are responsible for fetching and setting up the core browser engine (e.g., Chromium). This is a critical step to ensure the automation environment has the required rendering capability.
- **Input:** The `result` string from the previous installation stage.
- **Output:** A `result` string confirming the download and setup status of the browser binary.
- **Next Stage:** Stage 4 flows to Stage 5, then to Stage 6.

### Stage 6: User Session Snapshot
- **Description:** Takes a detailed snapshot of the current browser session state. The use of `--session user`, `-i` (interactive/inspect), and `--json` flags indicates this stage extracts structured data (likely DOM elements, cookies, or network data) from the active session in JSON format.
- **Input:** The `result` string from the browser setup stage.
- **Output:** A `result` string containing a JSON-formatted snapshot of the session data. This is often the key data product of the pipeline.
- **Next Stage:** Output flows to Stage 7.

### Stage 7: Final Page Load
- **Description:** Re-opens the target URL (`https://example.com`). This may serve to verify stability after setup, perform a fresh data extraction, or reset the session state for the next pipeline cycle.
- **Input:** The `result` (JSON snapshot) from Stage 6.
- **Output:** A `result` string with the final page load status, marking the end of the pipeline cycle.
- **Next Stage:** This is the final stage. The pipeline can loop back to Stage 1 to begin a new iteration.

## Data Flow & Iteration

The pipeline implements a linear data flow: `Stage 1 -> Stage 2 -> Stage 3 -> Stage 4 -> Stage 5 -> Stage 6 -> Stage 7`. The `result` output of each stage is passed as the primary data context to the next.

After Stage 7 completes, the pipeline logic resets, allowing it to start again at Stage 1. This enables continuous operation for tasks like periodic monitoring, repeated data extraction, or environment stress testing.

*Note: This tool is designed for security research and red team testing in authorized environments only.*
```