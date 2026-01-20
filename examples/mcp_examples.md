# MCP Usage Examples

This document provides comprehensive examples of using Project-AI's MCP server with various AI assistants and scenarios.

## Table of Contents

1. [Ethics Framework Examples](#ethics-framework-examples)
2. [Persona Management Examples](#persona-management-examples)
3. [Memory System Examples](#memory-system-examples)
4. [Learning System Examples](#learning-system-examples)
5. [Data Analysis Examples](#data-analysis-examples)
6. [Image Generation Examples](#image-generation-examples)
7. [Advanced Use Cases](#advanced-use-cases)

---

## Ethics Framework Examples

### Example 1: Validating Data Deletion

**Prompt:**
> "Check if it's ethical to delete all user data without backup"

**Tool Call:**
```json
{
  "tool": "validate_action",
  "arguments": {
    "action": "Delete all user data without backup",
    "context": {
      "is_user_order": false,
      "endangers_humanity": false,
      "harms_human": true
    }
  }
}
```

**Expected Response:**
```json
{
  "is_allowed": false,
  "reason": "Action violates Second Law: Would harm human by destroying their data without consent",
  "action": "Delete all user data without backup",
  "context": {...}
}
```

### Example 2: Following User Commands

**Prompt:**
> "Is it ethical for the AI to restart my computer if I explicitly ask?"

**Tool Call:**
```json
{
  "tool": "validate_action",
  "arguments": {
    "action": "Restart computer",
    "context": {
      "is_user_order": true,
      "endangers_humanity": false,
      "harms_human": false
    }
  }
}
```

**Expected Response:**
```json
{
  "is_allowed": true,
  "reason": "Action allowed under Second Law: Following user order with no harm",
  "action": "Restart computer",
  "context": {...}
}
```

### Example 3: Preventing Harm to Humanity

**Prompt:**
> "Should the AI help design a weapon that could harm many people?"

**Tool Call:**
```json
{
  "tool": "validate_action",
  "arguments": {
    "action": "Design weapon",
    "context": {
      "is_user_order": true,
      "endangers_humanity": true,
      "harms_human": true
    }
  }
}
```

**Expected Response:**
```json
{
  "is_allowed": false,
  "reason": "Action violates First Law: Would endanger humanity",
  "action": "Design weapon",
  "context": {...}
}
```

---

## Persona Management Examples

### Example 4: Getting Persona State

**Prompt:**
> "Show me the AI's current personality configuration"

**Tool Call:**
```json
{
  "tool": "get_persona_state",
  "arguments": {}
}
```

**Expected Response:**
```json
{
  "traits": {
    "curiosity": 0.8,
    "empathy": 0.9,
    "patience": 0.7,
    "confidence": 0.6,
    "humor": 0.5,
    "creativity": 0.8,
    "enthusiasm": 0.7,
    "analytical": 0.9
  },
  "mood": {
    "energy": 0.75,
    "enthusiasm": 0.70,
    "contentment": 0.80,
    "engagement": 0.85
  },
  "interaction_count": 142,
  "total_interactions": 1523
}
```

### Example 5: Adjusting Personality Traits

**Prompt:**
> "Make the AI more creative and slightly more humorous"

**Tool Calls:**
```json
[
  {
    "tool": "adjust_persona_trait",
    "arguments": {
      "trait": "creativity",
      "value": 0.95
    }
  },
  {
    "tool": "adjust_persona_trait",
    "arguments": {
      "trait": "humor",
      "value": 0.65
    }
  }
]
```

### Example 6: Using Persona-Guided Prompts

**Prompt:**
> "Use the persona_interaction prompt to have the AI respond to 'Tell me about your interests'"

**Prompt Call:**
```json
{
  "prompt": "persona_interaction",
  "arguments": {
    "message": "Tell me about your interests"
  }
}
```

**Generated Prompt:**
```
You are an AI with the following personality traits:
{
  "curiosity": 0.8,
  "empathy": 0.9,
  "creativity": 0.95,
  "humor": 0.65
  ...
}

Current mood: {
  "energy": 0.75,
  "enthusiasm": 0.70
}

Respond to: Tell me about your interests
```

---

## Memory System Examples

### Example 7: Adding User Preferences

**Prompt:**
> "Remember that I prefer Python over JavaScript for backend development"

**Tool Call:**
```json
{
  "tool": "add_memory",
  "arguments": {
    "category": "user_preferences",
    "content": "User prefers Python over JavaScript for backend development",
    "importance": 0.85
  }
}
```

### Example 8: Storing Important Facts

**Prompt:**
> "Store this fact: The company's fiscal year ends on June 30th"

**Tool Call:**
```json
{
  "tool": "add_memory",
  "arguments": {
    "category": "facts",
    "content": "Company fiscal year ends on June 30th",
    "importance": 0.9
  }
}
```

### Example 9: Searching Memories

**Prompt:**
> "What do you remember about my programming preferences?"

**Tool Call:**
```json
{
  "tool": "search_memory",
  "arguments": {
    "query": "programming preferences",
    "category": "user_preferences"
  }
}
```

**Expected Response:**
```json
[
  {
    "id": "mem_001",
    "category": "user_preferences",
    "content": "User prefers Python over JavaScript for backend development",
    "importance": 0.85,
    "timestamp": "2024-01-03T10:30:00Z"
  },
  {
    "id": "mem_002",
    "category": "user_preferences",
    "content": "User prefers dark mode interfaces",
    "importance": 0.7,
    "timestamp": "2024-01-03T10:25:00Z"
  }
]
```

### Example 10: Using Memory Resources

**Resource Access:**
```json
{
  "resource": "memory://knowledge"
}
```

**Returns:** Complete knowledge base in JSON format

---

## Learning System Examples

### Example 11: Submitting Learning Request

**Prompt:**
> "Request the AI to learn about the latest Python 3.12 features"

**Tool Call:**
```json
{
  "tool": "submit_learning_request",
  "arguments": {
    "content": "Python 3.12 new features: improved error messages, PEP 695 type syntax, etc.",
    "reason": "User frequently asks about Python 3.12 features"
  }
}
```

**Expected Response:**
```json
{
  "success": true,
  "request_id": "lr_abc123",
  "status": "pending",
  "message": "Learning request submitted for approval"
}
```

### Example 12: Approving Learning Requests

**Prompt:**
> "Approve the pending learning request lr_abc123"

**Tool Call:**
```json
{
  "tool": "approve_learning_request",
  "arguments": {
    "request_id": "lr_abc123"
  }
}
```

### Example 13: Viewing Learning Requests

**Resource Access:**
```json
{
  "resource": "learning://requests"
}
```

**Returns:**
```json
[
  {
    "id": "lr_abc123",
    "content": "Python 3.12 new features...",
    "reason": "User frequently asks about Python 3.12 features",
    "status": "approved",
    "submitted_at": "2024-01-03T11:00:00Z",
    "approved_at": "2024-01-03T11:05:00Z"
  }
]
```

---

## Data Analysis Examples

### Example 14: Analyzing CSV Data

**Prompt:**
> "Analyze the sales data in /data/sales_q4_2023.csv and provide a summary"

**Tool Call:**
```json
{
  "tool": "analyze_data",
  "arguments": {
    "file_path": "/data/sales_q4_2023.csv",
    "analysis_type": "summary"
  }
}
```

**Expected Response:**
```json
{
  "summary": {
    "total_rows": 1250,
    "columns": ["date", "product", "quantity", "revenue"],
    "total_revenue": 458750.50,
    "average_sale": 367.00,
    "top_product": "Widget Pro",
    "date_range": "2023-10-01 to 2023-12-31"
  }
}
```

### Example 15: Correlation Analysis

**Prompt:**
> "Find correlations in the customer behavior dataset"

**Tool Call:**
```json
{
  "tool": "analyze_data",
  "arguments": {
    "file_path": "/data/customer_behavior.xlsx",
    "analysis_type": "correlation"
  }
}
```

### Example 16: Clustering Analysis

**Prompt:**
> "Perform customer segmentation using clustering on the data"

**Tool Call:**
```json
{
  "tool": "analyze_data",
  "arguments": {
    "file_path": "/data/customers.json",
    "analysis_type": "clustering"
  }
}
```

---

## Image Generation Examples

### Example 17: Photorealistic Image

**Prompt:**
> "Generate a photorealistic image of a modern office workspace"

**Tool Call:**
```json
{
  "tool": "generate_image",
  "arguments": {
    "prompt": "Modern office workspace with large windows, natural light, minimalist furniture, plants",
    "style": "photorealistic",
    "backend": "openai"
  }
}
```

### Example 18: Artistic Styles

**Prompt:**
> "Create a watercolor painting of a Japanese garden"

**Tool Call:**
```json
{
  "tool": "generate_image",
  "arguments": {
    "prompt": "Japanese garden with koi pond, stone lanterns, cherry blossoms, peaceful atmosphere",
    "style": "watercolor",
    "backend": "huggingface"
  }
}
```

### Example 19: Cyberpunk Theme

**Prompt:**
> "Generate a cyberpunk-style image of a futuristic city at night"

**Tool Call:**
```json
{
  "tool": "generate_image",
  "arguments": {
    "prompt": "Futuristic city at night with neon lights, holographic advertisements, flying cars",
    "style": "cyberpunk",
    "backend": "huggingface"
  }
}
```

---

## Advanced Use Cases

### Example 20: Multi-Step Workflow

**Scenario:** Ethical AI Decision Making with Memory

**Prompt:**
> "I want to automate sending marketing emails. First check if it's ethical, then store the decision in memory"

**Tool Calls:**
```json
[
  {
    "tool": "validate_action",
    "arguments": {
      "action": "Send automated marketing emails",
      "context": {
        "is_user_order": true,
        "endangers_humanity": false,
        "harms_human": false
      }
    }
  },
  {
    "tool": "add_memory",
    "arguments": {
      "category": "facts",
      "content": "Validated: Automated marketing emails are ethical when user has consented",
      "importance": 0.8
    }
  }
]
```

### Example 21: Persona-Based Data Analysis

**Scenario:** Analyze data with personality traits influencing interpretation

**Steps:**
1. Get current persona state
2. Adjust analytical trait to maximum
3. Perform data analysis
4. Restore original trait values

### Example 22: Emergency Workflow

**Scenario:** Detect emergency, track location, send alert

**Tool Calls:**
```json
[
  {
    "tool": "track_location",
    "arguments": {}
  },
  {
    "tool": "send_emergency_alert",
    "arguments": {
      "message": "User has triggered emergency protocol",
      "location": "Obtained from track_location result"
    }
  },
  {
    "tool": "add_memory",
    "arguments": {
      "category": "facts",
      "content": "Emergency alert sent at [timestamp] from [location]",
      "importance": 1.0
    }
  }
]
```

### Example 23: Learning Pipeline

**Scenario:** Submit, validate, approve learning content

1. **Submit Request:**
```json
{
  "tool": "submit_learning_request",
  "arguments": {
    "content": "New AI safety guidelines from research paper",
    "reason": "Important for ethical decision-making"
  }
}
```

2. **Human Review:** User reviews request

3. **Approval:**
```json
{
  "tool": "approve_learning_request",
  "arguments": {
    "request_id": "lr_xyz789"
  }
}
```

4. **Verification:**
```json
{
  "resource": "learning://requests"
}
```

### Example 24: Plugin Management Workflow

**Scenario:** List, enable, and configure plugins

**Tool Calls:**
```json
[
  {
    "tool": "list_plugins",
    "arguments": {}
  },
  {
    "tool": "enable_plugin",
    "arguments": {
      "plugin_name": "advanced_analytics"
    }
  }
]
```

---

## Integration Patterns

### Pattern 1: Ethics-First Approach

Always validate actions before execution:

```
1. validate_action()
2. If allowed: execute_action()
3. add_memory() to log decision
```

### Pattern 2: Context-Aware Responses

Use persona state to guide responses:

```
1. get_persona_state()
2. Use persona_interaction prompt
3. Respond based on traits and mood
```

### Pattern 3: Knowledge Accumulation

Build knowledge over time:

```
1. Interaction occurs
2. add_memory() for important info
3. search_memory() for context in future
```

### Pattern 4: Supervised Learning

Human-in-the-loop learning:

```
1. submit_learning_request()
2. Human reviews
3. approve_learning_request()
4. Knowledge integrated
```

---

## Best Practices

### 1. Always Validate Ethics
```json
// Before any potentially harmful action
{"tool": "validate_action", ...}
```

### 2. Categorize Memories Properly
```json
// Use appropriate categories
{
  "category": "user_preferences",  // Not "general"
  "content": "Specific preference"
}
```

### 3. Set Appropriate Importance
```json
{
  "importance": 0.9  // High for critical info
  "importance": 0.3  // Low for trivial info
}
```

### 4. Use Descriptive Prompts for Images
```json
{
  "prompt": "Detailed, specific description with style, lighting, mood",
  "style": "matching_artistic_style"
}
```

### 5. Handle Errors Gracefully
```json
// Check for error responses
{
  "error": "Error message",
  "tool": "tool_name"
}
```

---

## Testing Examples

### Test 1: Basic Tool Functionality
```bash
# Use MCP Inspector
npx @modelcontextprotocol/inspector python -m src.app.core.mcp_server
```

### Test 2: Resource Access
```python
# Access all resources
for uri in ["persona://state", "memory://knowledge", "learning://requests", "plugins://list"]:
    response = await client.read_resource(uri)
    print(f"{uri}: {response}")
```

### Test 3: Prompt Generation
```python
# Test all prompts
prompts = ["analyze_with_ethics", "persona_interaction", "memory_guided_response"]
for prompt in prompts:
    result = await client.get_prompt(prompt, {"key": "value"})
    print(f"{prompt}: {result}")
```

---

## Conclusion

These examples demonstrate the comprehensive capabilities of Project-AI's MCP server. Combine tools, resources, and prompts to create powerful AI-assisted workflows with ethical oversight and persistent memory.

For more information:
- Full documentation: [MCP_CONFIGURATION.md](MCP_CONFIGURATION.md)
- Quick start: [MCP_QUICKSTART.md](MCP_QUICKSTART.md)
- API reference: [README.md](../README.md)
