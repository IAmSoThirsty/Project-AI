# Writer-Reviewer Content Collaboration Workflow

A multi-agent workflow built with **Microsoft Agent Framework** that enables collaborative content creation through a Writer and Reviewer agent working together.

## Overview

This application demonstrates a sequential multi-agent workflow where:
1. **Writer Agent** receives user content requests and creates initial drafts
2. **Reviewer Agent** analyzes the content and provides actionable feedback
3. Both agents' outputs are combined into a final collaborative result

## Architecture

- **Framework**: Microsoft Agent Framework (Python)
- **Protocol**: OpenAI-compatible `responses` API
- **Hosting**: Foundry-compatible HTTP server on port 8088
- **Agents**: 
  - `WriterAgent` - Content creation specialist
  - `ReviewerAgent` - Content quality reviewer

## Prerequisites

- Python 3.12+
- Azure AI Foundry project with a deployed model (e.g., GPT-4o)
- Azure credentials configured (Azure CLI or environment variables)

## Installation

### 1. Create Virtual Environment

```bash
python -m venv .venv
```

### 2. Activate Virtual Environment

**Windows:**
```powershell
.\.venv\Scripts\Activate.ps1
```

**macOS/Linux:**
```bash
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## Configuration

### 1. Copy Environment Template

```bash
cp .env.example .env
```

### 2. Configure Environment Variables

Edit `.env` and set:

```bash
# Your Azure AI Foundry project endpoint
FOUNDRY_PROJECT_ENDPOINT=https://your-project.openai.azure.com/

# Your deployed model name
FOUNDRY_MODEL_DEPLOYMENT_NAME=gpt-4o
```

### 3. Azure Authentication

The application uses `DefaultAzureCredential` for local development. Ensure you're authenticated via:

```bash
az login
```

## Usage

### Start the Workflow Server

```bash
python app.py
```

The server will start on `http://localhost:8088`

### Send Content Requests

**Using curl:**

```bash
curl -X POST http://localhost:8088/responses \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user",
        "content": "Write a blog post introduction about the benefits of AI in healthcare"
      }
    ]
  }'
```

**Example Response:**

```
=== WRITER-REVIEWER COLLABORATION OUTPUT ===

INITIAL CONTENT (by Writer):
Artificial Intelligence is revolutionizing healthcare delivery...
[Writer's full content]

---

REVIEW & FEEDBACK (by Reviewer):
1. Strengthen the opening hook to immediately engage readers
2. Add specific examples of AI applications in healthcare
3. Consider addressing potential concerns about AI in medical settings
[Reviewer's detailed feedback]

=== END OF COLLABORATION ===
```

## Workflow Details

### Writer Agent Instructions

- Understands user content requests
- Creates well-structured, engaging initial content
- Focuses on clarity, coherence, and completeness
- Professional yet accessible tone

### Reviewer Agent Instructions

- Carefully reviews provided content
- Identifies improvement areas (clarity, structure, completeness, tone)
- Provides concise, actionable feedback
- Suggests specific refinements

### Execution Flow

```
User Request → Writer Agent → Reviewer Agent → Formatted Output
```

## Deployment to Azure AI Foundry

Ready to deploy to production? Use the Foundry deployment workflow:

### 1. Build Docker Image

```bash
docker build --platform linux/amd64 -t writer-reviewer-workflow:latest .
```

### 2. Deploy to Foundry

Reply with **"Deploy agent to Foundry"** to start the deployment process.

## Project Structure

```
writer-reviewer-workflow/
├── app.py                  # Main application with Writer & Reviewer agents
├── agent.yaml              # Foundry agent metadata
├── requirements.txt        # Python dependencies
├── Dockerfile              # Container definition
├── .env                    # Environment configuration (create from .env.example)
├── .env.example            # Environment template
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

## Key Features

✅ **Multi-Agent Orchestration** - Sequential workflow graph with Writer → Reviewer  
✅ **Graph-Based Execution** - Built on Agent Framework's graph orchestration  
✅ **Output Executors** - Both agents contribute to final collaborative output  
✅ **Foundry-Ready** - HTTP server mode for local testing and cloud deployment  
✅ **Production Auth** - Managed Identity support for Azure deployment  
✅ **Structured Logging** - Comprehensive logging for debugging and monitoring  

## Customization

### Modify Agent Instructions

Edit the `instructions` parameter in `WriterAgent` and `ReviewerAgent` classes in `app.py`.

### Change Model

Update `FOUNDRY_MODEL_DEPLOYMENT_NAME` in `.env` to use a different model deployment.

### Add More Agents

Extend the workflow graph by:
1. Creating new agent classes inheriting from `BaseAgent`
2. Adding nodes to the graph in `build_workflow()`
3. Defining edges between agents

### Adjust Output Format

Modify the `format_output()` function in `build_workflow()` to change how results are presented.

## Troubleshooting

### Common Issues

**Issue**: `ModuleNotFoundError: No module named 'agent_framework'`  
**Solution**: Ensure virtual environment is activated and dependencies are installed:
```bash
.venv\Scripts\Activate.ps1  # Windows
pip install -r requirements.txt
```

**Issue**: `ValueError: FOUNDRY_PROJECT_ENDPOINT environment variable is required`  
**Solution**: Configure `.env` file with your Azure AI Foundry project endpoint.

**Issue**: `DefaultAzureCredential failed to retrieve a token`  
**Solution**: Authenticate with Azure CLI:
```bash
az login
```

**Issue**: Port 8088 already in use  
**Solution**: Stop other services on port 8088 or modify the port in the hosting adapter configuration.

## Next Steps

1. **Test Locally** - Run the workflow and test with different content requests
2. **Enable Debugging** - Configure VS Code debugging with AI Toolkit Agent Inspector
3. **Add Tracing** - Integrate Application Insights for production monitoring
4. **Run Evaluations** - Set up batch evaluations to measure content quality
5. **Deploy to Foundry** - Containerize and deploy for production use

## Resources

- [Microsoft Agent Framework Docs](https://learn.microsoft.com/agent-framework/overview/agent-framework-overview)
- [Azure AI Foundry](https://ai.azure.com)
- [Agent Framework GitHub](https://github.com/microsoft/agent-framework)
- [Foundry Hosted Agents](https://learn.microsoft.com/azure/ai-foundry/agents/concepts/hosted-agents)

## License

MIT
