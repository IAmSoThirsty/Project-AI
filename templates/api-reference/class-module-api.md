---
title: "API: <% tp.file.title %>"
created: <% tp.date.now("YYYY-MM-DD") %>
type: documentation
doc_type: api-reference
template_type: api-documentation
class_name: <% tp.system.prompt("Class/Module name") %>
language: <% tp.system.suggester(["Python", "JavaScript", "TypeScript", "Java", "Go", "Rust", "C++"], ["python", "javascript", "typescript", "java", "go", "rust", "cpp"]) %>
api_type: <% tp.system.suggester(["Class", "Module", "Interface", "Type", "Namespace"], ["class", "module", "interface", "type", "namespace"]) %>
status: <% tp.system.suggester(["✅ Stable", "🚧 Beta", "⚠️ Deprecated"], ["stable", "beta", "deprecated"]) %>
tags: [template, api-reference, class-api, code-api, templater, <% tp.frontmatter.language %>]
last_verified: <% tp.date.now("YYYY-MM-DD") %>
template_status: current
stakeholders: [developers, api-team]
complexity_level: intermediate
estimated_completion: 20
requires: [templater-plugin]
review_cycle: quarterly
---

# 📦 Class API: <% tp.file.title %>

## Overview
**Class:** `<% tp.frontmatter.class_name %>`  
**Language:** <% tp.frontmatter.language %>  
**Type:** <% tp.frontmatter.api_type %>  
**Module:** `<% tp.system.prompt("Module path") %>`  
**Status:** <% tp.frontmatter.status %>

### Purpose
<% tp.system.prompt("Class purpose (1-2 sentences)") %>

### Import
```<% tp.frontmatter.language %>
from <% tp.system.prompt("module") %> import <% tp.frontmatter.class_name %>
```

---

## Constructor

### `__init__()` / `constructor()`

```<% tp.frontmatter.language %>
def __init__(
    self,
    param1: <% tp.system.prompt("param1 type") %>,
    param2: <% tp.system.prompt("param2 type") %>,
    **kwargs
):
    """
    <% tp.system.prompt("Constructor description") %>
    
    Args:
        param1: <% tp.system.prompt("param1 description") %>
        param2: <% tp.system.prompt("param2 description") %>
        **kwargs: Optional keyword arguments
    
    Raises:
        ValueError: <% tp.system.prompt("When raised") %>
    """
```

**Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `<% tp.system.prompt("param1") %>` | <% tp.system.prompt("type") %> | ✓ | N/A | <% tp.system.prompt("Description") %> |

**Example:**
```<% tp.frontmatter.language %>
instance = <% tp.frontmatter.class_name %>(
    param1=<% tp.system.prompt("value1") %>,
    param2=<% tp.system.prompt("value2") %>
)
```

---

## Attributes

### Instance Attributes
| Attribute | Type | Access | Description |
|-----------|------|--------|-------------|
| `<% tp.system.prompt("attr1") %>` | <% tp.system.prompt("type") %> | Public | <% tp.system.prompt("Description") %> |
| `attr2` | type | Private | Description |

### Class Attributes
| Attribute | Type | Description |
|-----------|------|-------------|
| `<% tp.system.prompt("CLASS_ATTR") %>` | <% tp.system.prompt("type") %> | <% tp.system.prompt("Description") %> |

---

## Methods

### Public Methods

#### `method_name(param1, param2) -> ReturnType`

```<% tp.frontmatter.language %>
def method_name(
    self,
    param1: <% tp.system.prompt("type") %>,
    param2: <% tp.system.prompt("type") %>
) -> <% tp.system.prompt("return_type") %>:
    """
    <% tp.system.prompt("Method description") %>
    
    Args:
        param1: <% tp.system.prompt("Description") %>
        param2: Description
    
    Returns:
        <% tp.system.prompt("Return description") %>
    
    Raises:
        ExceptionType: When condition
    
    Example:
        >>> obj = <% tp.frontmatter.class_name %>()
        >>> result = obj.method_name(param1, param2)
        >>> print(result)
        expected_output
    """
```

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `param1` | type | ✓ | Description |

**Returns:** <% tp.system.prompt("Return value description") %>

**Example:**
```<% tp.frontmatter.language %>
result = instance.method_name(value1, value2)
```

---

### Static Methods

#### `@staticmethod utility_method(param) -> ReturnType`

```<% tp.frontmatter.language %>
@staticmethod
def utility_method(param: <% tp.system.prompt("type") %>) -> <% tp.system.prompt("return_type") %>:
    """
    <% tp.system.prompt("Static method description") %>
    
    Args:
        param: Description
    
    Returns:
        Description
    """
```

---

### Class Methods

#### `@classmethod from_dict(cls, data) -> Class`

```<% tp.frontmatter.language %>
@classmethod
def from_dict(cls, data: dict) -> '<% tp.frontmatter.class_name %>':
    """
    Create instance from dictionary.
    
    Args:
        data: Dictionary with initialization data
    
    Returns:
        New instance of <% tp.frontmatter.class_name %>
    """
```

---

## Properties

### `property_name`

```<% tp.frontmatter.language %>
@property
def property_name(self) -> <% tp.system.prompt("type") %>:
    """<% tp.system.prompt("Property description") %>"""
    return self._property_name

@property_name.setter
def property_name(self, value: <% tp.system.prompt("type") %>):
    """Set property value with validation."""
    # Validation logic
    self._property_name = value
```

---

## Special Methods (Dunder/Magic Methods)

| Method | Purpose | Example |
|--------|---------|---------|
| `__str__()` | String representation | `str(obj)` |
| `__repr__()` | Developer representation | `repr(obj)` |
| `__len__()` | Length/size | `len(obj)` |
| `__eq__()` | Equality comparison | `obj1 == obj2` |

---

## Usage Examples

### Basic Usage
```<% tp.frontmatter.language %>
# Create instance
obj = <% tp.frontmatter.class_name %>(param1, param2)

# Use methods
result = obj.method_name(arg1, arg2)

# Access properties
value = obj.property_name
```

### Advanced Usage
```<% tp.frontmatter.language %>
# With context manager
with <% tp.frontmatter.class_name %>(param1, param2) as obj:
    result = obj.method_name(arg)

# From dict
data = {"param1": "value1", "param2": "value2"}
obj = <% tp.frontmatter.class_name %>.from_dict(data)
```

---

## Inheritance

**Base Classes:** <% tp.system.prompt("Base classes (e.g., BaseClass, Interface)", "object") %>

**Inheritance Diagram:**
```
object
  └── <% tp.frontmatter.class_name %>
```

**Overridden Methods:**
| Method | Base Class | Description |
|--------|------------|-------------|
| `method()` | BaseClass | Customization details |

---

## Type Annotations (TypeScript/TypedDict)

```<% tp.frontmatter.language %>
# Type definition
class <% tp.frontmatter.class_name %>Protocol:
    param1: <% tp.system.prompt("type") %>
    param2: <% tp.system.prompt("type") %>
    
    def method_name(self, arg: type) -> type: ...
```

---

## Testing

### Test Example
```<% tp.frontmatter.language %>
def test_<% tp.frontmatter.class_name.lower() %>():
    """Test basic functionality."""
    obj = <% tp.frontmatter.class_name %>(param1, param2)
    result = obj.method_name(arg)
    
    assert result == expected
    assert obj.property_name == expected_value
```

---

## Performance

**Time Complexity:**
| Method | Complexity |
|--------|------------|
| `method_name()` | O(<% tp.system.prompt("complexity (e.g., 1, n, log n)", "1") %>) |

**Space Complexity:** O(<% tp.system.prompt("complexity", "1") %>)

---

## Related Classes
- [[<% tp.system.prompt("Related class 1") %>]] - Description
- [[Related class 2]] - Description

---

**Last Updated:** <% tp.date.now("YYYY-MM-DD HH:mm") %>  
*Template: `templates/api-reference/class-module-api.md`*
