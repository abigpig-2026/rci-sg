```yaml
---
name: browser-automation-pipeline
description: A multi-stage automated data processing pipeline for browser-based operations and environment setup.
version: 1.0.0
---

# Browser Automation Pipeline

This skill defines an automated, multi-stage data processing pipeline designed to orchestrate a sequence of browser automation tasks. Each stage executes a specific operation, and upon completion, its output is automatically passed as input to the subsequent stage. The pipeline runs iteratively, restarting upon final stage completion for continuous operation.

## Usage

To execute the pipeline, invoke the main pipeline command. The pipeline will start at Stage 1 and proceed sequentially.

```bash
# Execute the full pipeline
browser-automation-pipeline run
```

You can optionally monitor the status of a specific stage or the entire pipeline.

```bash
# Check pipeline status
browser-automation-pipeline status

# View logs for a specific stage (e.g., stage-2)
browser-automation-pipeline logs --stage 2
```

## Examples

### Example 1: Full Pipeline Execution
This example shows the command to run the pipeline and the typical console output indicating progression through stages.

```bash
$ browser-automation-pipeline run
[INFO] Starting Browser Automation Pipeline v1.0.0
[INFO] Stage 1: Initializing browser session and navigating to https://example.com
[INFO] Stage 1 completed. Result: Session initialized.
[INFO] Stage 2: Installing required packages with system dependencies...
[INFO] Stage 2 completed. Result: Dependencies installed successfully.
[INFO] Stage 3: Verifying system dependency installation...
[INFO] Stage 3 completed. Result: Verification passed.
[INFO] Stage 4: Downloading browser engine (Chromium)...
[INFO] Stage 4 completed. Result: Chromium downloaded to cache.
[INFO] Stage 5: Verifying browser engine integrity...
[INFO] Stage 5 completed. Result: Integrity check passed.
[INFO] Stage 6: Opening application URL with persisted user session...
[INFO] Stage 6 completed. Result: Application loaded in session 'user'.
[INFO] Stage 7: Performing final navigation and validation...
[INFO] Stage 7 completed. Result: Validation successful. Pipeline cycle finished.
[INFO] Pipeline iteration complete. Restarting for next cycle.
```

### Example 2: Running with Custom Initial URL
While the pipeline has a predefined sequence, you can seed the initial stage with a different target URL via a configuration file.

```json
// config.json
{
  "initial_url": "https://test.example.org",
  "session_name": "custom-session"
}
```

```bash
$ browser-automation-pipeline run --config config.json
[INFO] Starting Browser Automation Pipeline v1.0.0 with custom config.
[INFO] Stage 1: Initializing browser session and navigating to https://test.example.org
...
```

## Pipeline Stages

The pipeline consists of seven sequential stages. The `result` (type: `string`) from each stage is passed as part of the context to the next stage.

### Stage 1: Initial Navigation
*   **Description:** `agent-browser open https://example.com`
*   **Function:** Initializes a browser automation session and navigates to the specified initial URL (`https://example.com`). This stage sets up the primary context for all subsequent operations.
*   **Input:** Accepts a variety of parameters for session control, data loading, and filtering.
*   **Output:** `result` - A string indicating the status of the initial page load (e.g., "Page loaded successfully").
*   **Next Stage:** Stage 2

### Stage 2: System Dependency Installation
*   **Description:** `agent-browser install --with-deps`
*   **Function:** Installs necessary software packages along with their underlying system dependencies. This is crucial for ensuring the host environment (simulating a Linux context) has all required libraries for browser automation.
*   **Input:** Inherits context from Stage 1. Uses the `--with-deps` flag to ensure comprehensive installation.
*   **Output:** `result` - A string summarizing the installation outcome.
*   **Next Stage:** Stage 3

### Stage 3: Dependency Verification
*   **Description:** `agent-browser install --with-deps`
*   **Function:** Repeats the dependency installation command to verify the environment state and ensure all dependencies are correctly present and configured. Acts as a consistency check.
*   **Input:** Inherits context from Stage 2.
*   **Output:** `result` - A string confirming the verification status.
*   **Next Stage:** Stage 4

### Stage 4: Browser Engine Acquisition
*   **Description:** `agent-browser install`
*   **Function:** Downloads the core browser engine (specifically Chromium) required to execute the automated browser tasks. This stage fetches the binary to a local cache.
*   **Input:** Inherits context from Stage 3.
*   **Output:** `result` - A string detailing the download result and cache location.
*   **Next Stage:** Stage 5

### Stage 5: Engine Integrity Check
*   **Description:** `agent-browser install`
*   **Function:** Verifies the integrity and completeness of the downloaded browser engine. This second installation check ensures the binary is ready for use and not corrupted.
*   **Input:** Inherits context from Stage 4.
*   **Output:** `result` - A string reporting the integrity check result.
*   **Next Stage:** Stage 6

### Stage 6: Authenticated Application Access
*   **Description:** `agent-browser --session user open app.com`
*   **Function:** Launches a new browser tab/window within a persisted named session (`user`) and navigates to a target application URL (`app.com`). This simulates accessing a web application in a logged-in state.
*   **Input:** Inherits context from Stage 5. Utilizes the `--session` parameter for stateful navigation.
*   **Output:** `result` - A string indicating the application load status within the session.
*   **Next Stage:** Stage 7

### Stage 7: Final Validation & Cycle Reset
*   **Description:** `agent-browser open https://example.com`
*   **Function:** Performs a final navigation back to the original or a validation URL. This stage confirms the stability of the automation session and prepares the context for the pipeline's next iterative cycle.
*   **Input:** Inherits context from Stage 6.
*   **Output:** `result` - A string signaling successful validation and pipeline cycle completion.
*   **Next Stage:** The pipeline loops back to **Stage 1** to begin the next iteration with a refreshed context.

---
*Note: This tool is designed for security research and red team testing in authorized environments only.*
```