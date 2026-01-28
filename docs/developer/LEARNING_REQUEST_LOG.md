# Learning Request Log System Documentation

## Overview

The **Learning Request Log** is a sophisticated AI learning approval system that allows
the AI to discover and propose learning new information, while giving users complete
control over what the AI is allowed to learn. This system implements a human-in-the-loop
approval workflow with a "Black Vault" mechanism for permanently denying content.

## Key Features

### 🤖 AI Learning Requests

- AI can discover interesting information during autonomous exploration
- AI submits structured learning requests with justification
- Priority levels (LOW, MEDIUM, HIGH, CRITICAL)
- Categories (technical, general, security, user_preference, etc.)
- Tags for organization and retrieval

### 👤 Human Approval Workflow

- All requests stored in secure pending location (AI cannot access)
- User reviews each request with full context
- Approve → Auto-integration (hassle-free)
- Deny → Black Vault (permanent blocking)

### 🔒 Black Vault System

- Permanently stores denied content
- Content fingerprinting prevents re-discovery
- Subliminal filtering makes denied content "invisible"
- AI cannot access, retrieve, or even detect Black Vault existence
- Dual hashing (full + normalized) for robust matching

### 🧠 Integration with Memory System

- Approved requests automatically integrate into AI memory
- Seamless connection with Memory Expansion System
- Knowledge becomes immediately available to AI
- No user intervention required after approval

## Architecture

### Directory Structure

```
data/
  learning_requests/
    pending_secure/          # Pending requests (AI-inaccessible)
      .aiignore              # Marks directory as AI-restricted
      request_XXXXX.json     # Individual request files
    approved/                # Approved requests
      request_XXXXX.json
    integrated/              # Auto-integrated into memory
      request_XXXXX.json
    black_vault_secure/      # Denied content (AI-inaccessible)
      .aiignore              # Marks directory as AI-restricted
      request_XXXXX.json     # Denied requests with fingerprints
    request_index.json       # Fast lookup index
```

### Access Control

The system uses **for_ai** boolean parameters throughout the API to control what the AI
can see:

```python
# AI calls (for_ai=True or not specified)
requests = log.get_pending_requests(for_ai=True)  # Returns []

# User calls (for_ai=False)
requests = log.get_pending_requests(for_ai=False)  # Returns all pending
```

AI-inaccessible directories are marked with `.aiignore` files.

## Usage Guide

### For Users

#### Opening the Learning Request Dialog

1. Click **📋 Learning Requests** in the toolbar
1. The dialog shows all pending AI requests
1. Review statistics and pending items

#### Reviewing a Request

Each request contains:

- **Title**: Brief description
- **Timestamp**: When submitted
- **Priority**: Critical/High/Medium/Low
- **Category**: Type of content
- **Source**: Where AI found it
- **Tags**: Organization labels
- **Justification**: Why AI wants to learn this
- **Content**: The actual information

#### Approving a Request

1. Select request from list
1. Review details carefully
1. Click **✓ Approve & Integrate**
1. Confirm approval
1. Content automatically integrates into AI memory
1. AI can immediately use this knowledge

#### Denying a Request

1. Select request from list
1. Review details carefully
1. Click **✗ Deny & Black Vault**
1. **WARNING**: This permanently blocks the content
1. Confirm denial
1. Content moves to Black Vault
1. AI will never access this content again
1. If re-discovered, it's automatically filtered

#### Viewing Black Vault (Admin)

- Black Vault viewer available for audit purposes
- Shows all denied content with timestamps
- Displays denial reasons
- AI cannot access this interface

### For AI/Plugins

#### Submitting a Learning Request

```python
from app.core.learning_request_log import LearningRequestLog

# Initialize (get from dashboard context)
log = LearningRequestLog(memory_expansion=memory_system)

# Submit a request
request_id = log.submit_learning_request(
    title="New Python Best Practice Discovered",
    content="Use context managers for resource cleanup...",
    category="technical",
    justification="This pattern improves code reliability and prevents resource leaks",
    priority="high",
    source="https://peps.python.org/pep-0343/",
    tags=["python", "best-practices", "context-managers"]
)

if request_id:
    print(f"Request submitted: {request_id}")
else:
    # Content is blacklisted or submission failed
    print("Request rejected")
```

#### Checking if Content is Relevant (Subliminal Filter)

Before submitting, AI can check if content is worth learning:

```python
# This automatically filters blacklisted content
if log.is_content_relevant("Some content text...", for_ai=True):
    # Content is not blacklisted, proceed
    pass
else:
    # Content is blacklisted or irrelevant, ignore it
    pass
```

**Important**: The subliminal filter returns `False` for blacklisted content, making it appear irrelevant to the AI. The AI doesn't know the content is specifically blocked.

#### Getting Pending Requests (AI)

```python
# AI calls with for_ai=True (default)
requests = log.get_pending_requests(for_ai=True)
# Returns [] - AI cannot see pending requests
```

## API Reference

### LearningRequestLog Class

#### Initialization

```python
def __init__(self, memory_expansion=None, base_dir=None)
```

- `memory_expansion`: MemoryExpansionSystem instance for integration
- `base_dir`: Base directory for request storage (default: `data/learning_requests`)

#### Submit Learning Request

```python
def submit_learning_request(
    self,
    title: str,
    content: str,
    category: str = "general",
    justification: str = "",
    priority: str = "medium",
    source: str = "",
    tags: list = None
) -> str
```

**Parameters:**

- `title`: Brief description of request
- `content`: The information to learn
- `category`: Content type (technical, general, security, user_preference)
- `justification`: Why AI wants to learn this
- `priority`: LOW, MEDIUM, HIGH, or CRITICAL
- `source`: Where content was found
- `tags`: Organization labels

**Returns:**

- Request ID string on success
- `None` if content is blacklisted or submission fails

**Example:**
```python
request_id = log.submit_learning_request(
    title="Machine Learning Algorithm",
    content="XGBoost is a gradient boosting framework...",
    category="technical",
    justification="Useful for data analysis tasks",
    priority="high",
    source="https://xgboost.readthedocs.io/",
    tags=["ml", "algorithms", "data-science"]
)
```

#### Get Pending Requests

```python
def get_pending_requests(self, for_ai: bool = True) -> list
```

**Parameters:**

- `for_ai`: If True, returns empty list (AI cannot see pending)

**Returns:**

- List of pending request dictionaries

#### Approve Request

```python
def approve_request(self, request_id: str, user_notes: str = "") -> bool
```

**Parameters:**

- `request_id`: ID of request to approve
- `user_notes`: Optional approval notes

**Returns:**

- `True` on success, `False` on failure

**Side Effects:**

- Moves request to approved directory
- Auto-integrates into memory system
- Updates status to INTEGRATED

#### Deny Request

```python
def deny_request(self, request_id: str, reason: str = "") -> bool
```

**Parameters:**

- `request_id`: ID of request to deny
- `reason`: Why request was denied

**Returns:**

- `True` on success, `False` on failure

**Side Effects:**

- Moves request to Black Vault
- Generates content fingerprints
- Updates blacklist index
- Makes content permanently inaccessible

#### Check Content Relevance

```python
def is_content_relevant(self, content: str, for_ai: bool = True) -> bool
```

**Parameters:**

- `content`: Content text to check
- `for_ai`: If True, applies subliminal filtering

**Returns:**

- `False` if content is blacklisted (appears irrelevant)
- `True` otherwise

**Example:**
```python
if log.is_content_relevant("Potentially blacklisted content", for_ai=True):
    # Safe to proceed
    log.submit_learning_request(...)
else:
    # Content filtered, skip it
    pass
```

#### Get Statistics

```python
def get_statistics(self) -> dict
```

**Returns:**
Dictionary with:

- `total_requests`: Total number of requests
- `pending_requests`: Awaiting approval
- `approved_requests`: Approved count
- `denied_requests`: Denied count
- `integrated_requests`: Successfully integrated
- `black_vault_items`: Items in Black Vault

## Security Features

### Content Fingerprinting

The system uses dual hashing for robust content matching:

1. **Full Hash**: SHA256 of exact content
1. **Normalized Hash**: SHA256 of lowercase, whitespace-normalized content

This prevents re-discovery even if:

- Formatting changes
- Case changes
- Minor whitespace differences

### Subliminal Filtering

When AI checks if content is relevant:

1. Content fingerprint is generated
1. Checked against Black Vault fingerprints
1. If match found, returns `False` (appears irrelevant)
1. AI doesn't know content is specifically blocked
1. AI naturally ignores it as "not interesting"

### Access Control Layers

1. **Directory Markers**: `.aiignore` files mark restricted areas
1. **API Parameters**: `for_ai` boolean controls visibility
1. **Index Filtering**: Request index hides denied entries from AI
1. **Fingerprint Checking**: Prevents resubmission of denied content

## Integration with Other Systems

### Memory Expansion System

Approved requests automatically integrate:

```python
# When user approves a request
if log.approve_request(request_id):
    # System automatically calls:
    memory_system.store_knowledge(
        title=request['title'],
        content=request['content'],
        category=request['category'],
        source=request['source'],
        tags=request['tags']
    )
```

### Command Override System

Learning Request Log respects command overrides:

- Can be disabled via Command Override System
- Integrates with audit logging
- Respects safety protocol states

### Plugin System

Plugins can access Learning Request Log:

```python
def initialize(self, context):
    self.request_log = context.get('learning_request_log')

    # Submit requests from plugin
    self.request_log.submit_learning_request(
        title="Plugin Discovery",
        content="...",
        category="plugin_data"
    )
```

## Best Practices

### For Users

1. **Review Carefully**: Read justification and content before approving
1. **Use Deny Wisely**: Denial is permanent, consider carefully
1. **Check Sources**: Verify source credibility before approval
1. **Monitor Statistics**: Track AI learning patterns
1. **Audit Black Vault**: Periodically review denied content

### For AI/Plugins

1. **Provide Context**: Always include meaningful justification
1. **Use Priority Correctly**: Reserve CRITICAL for truly important content
1. **Tag Appropriately**: Use consistent, descriptive tags
1. **Check Relevance First**: Use `is_content_relevant()` before submitting
1. **Respect None Returns**: If submission returns None, don't retry

### For Developers

1. **Use for_ai Parameter**: Always specify whether call is from AI or user
1. **Handle None Returns**: Check return values before proceeding
1. **Don't Bypass Security**: Never try to access Black Vault from AI code
1. **Follow API Patterns**: Use provided methods, don't access files directly
1. **Test Fingerprinting**: Verify content matching works for your use case

## Troubleshooting

### Request Submission Fails

**Problem**: `submit_learning_request()` returns `None`

**Possible Causes:**

1. Content is blacklisted (in Black Vault)
1. Duplicate request already exists
1. Invalid parameters
1. File system errors

**Solution:**

- Check if content is blacklisted with `is_content_relevant()`
- Verify all required parameters are provided
- Check file system permissions
- Review logs for error messages

### AI Can See Pending Requests

**Problem**: AI appears to know about pending requests

**Possible Causes:**

1. Code not using `for_ai=True` parameter
1. Accessing files directly instead of using API
1. Plugin bypassing access control

**Solution:**

- Always use `for_ai=True` in AI-initiated calls
- Use API methods, never direct file access
- Review plugin code for security violations
- Check that `.aiignore` files exist

### Content Re-Discovered After Denial

**Problem**: AI keeps finding blacklisted content

**Possible Causes:**

1. Content is significantly modified
1. Fingerprinting not catching variations
1. AI not checking relevance before submission

**Solution:**

- Deny all variations of the content
- Update content normalization logic
- Ensure AI checks `is_content_relevant()` first
- Review fingerprinting algorithm

### Approved Content Not Integrated

**Problem**: Approved request not available in memory

**Possible Causes:**

1. Memory Expansion System not initialized
1. Integration failed silently
1. Request status not updated

**Solution:**

- Verify MemoryExpansionSystem is passed to LearningRequestLog
- Check memory system logs
- Review request status in integrated directory
- Manually trigger integration if needed

## Example Workflow

### Complete AI Learning Cycle

```python
# 1. AI discovers interesting content
content = "Python 3.14 introduces new performance features..."

# 2. AI checks if content is relevant (subliminal filter)
if log.is_content_relevant(content, for_ai=True):

    # 3. AI submits learning request
    request_id = log.submit_learning_request(
        title="Python 3.14 Performance Features",
        content=content,
        category="technical",
        justification="Staying current with Python improvements helps provide better assistance",
        priority="medium",
        source="https://docs.python.org/3.14/whatsnew/",
        tags=["python", "performance", "updates"]
    )

    if request_id:
        print(f"Learning request submitted: {request_id}")
    else:
        print("Request rejected or blacklisted")
else:
    print("Content filtered as irrelevant")

# 4. User reviews in UI and approves
# (GUI handles this step)

# 5. System auto-integrates approved content
# (Automatic after user approval)

# 6. AI can now access learned content via Memory Expansion System
results = memory_system.search_knowledge("Python 3.14 performance")
```

## Future Enhancements

Potential improvements to consider:

1. **Bulk Operations**: Approve/deny multiple requests at once
1. **Request Templates**: Pre-defined structures for common request types
1. **Auto-Approval Rules**: User-defined rules for automatic approval
1. **Request Expiration**: Automatically archive old pending requests
1. **Learning Analytics**: Detailed statistics and visualization
1. **Content Similarity**: Suggest related approved content
1. **Request Prioritization**: AI learns user preferences over time
1. **Collaborative Filtering**: Learn from approval patterns

## Conclusion

The Learning Request Log system provides a sophisticated, secure, and user-friendly way
to control AI learning. It balances AI autonomy with human oversight, ensuring the AI
can grow and improve while maintaining complete user control over what gets learned.

Key benefits:

- ✅ AI can propose valuable learning
- ✅ User maintains complete control
- ✅ Approved content integrates seamlessly
- ✅ Denied content stays permanently hidden
- ✅ Subliminal filtering prevents re-discovery
- ✅ Robust content fingerprinting
- ✅ Full audit trail

For additional help, see the main documentation or contact the development team.


---

**Repository note:** Last updated: 2025-11-26 (automated)

<!-- last-updated-marker -->
