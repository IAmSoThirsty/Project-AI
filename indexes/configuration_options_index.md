# Configuration Options Index

> **📍 Location**: `indexes/configuration_options_index.md`  
> **🎯 Purpose**: Index of all configuration parameters and environment variables  
> **👥 Audience**: DevOps, system administrators  
> **🔄 Status**: Production-Ready ✓

---

## 🔐 Required Environment Variables

| Variable | Purpose | Type | Default | Example | Documentation |
|----------|---------|------|---------|---------|---------------|
| `OPENAI_API_KEY` | OpenAI API access | Secret | None | `sk-...` | [[.env.example|Template]] |
| `HUGGINGFACE_API_KEY` | Hugging Face API | Secret | None | `hf_...` | [[.env.example|Template]] |

---

## ⚙️ Optional Environment Variables

| Variable | Purpose | Type | Default | Example | Documentation |
|----------|---------|------|---------|---------|---------------|
| `FERNET_KEY` | Encryption key | Secret | Generated | `...` | [[.env.example|Template]] |
| `SMTP_USERNAME` | Email alerts | String | None | `user@example.com` | [[.env.example|Template]] |
| `SMTP_PASSWORD` | Email password | Secret | None | `...` | [[.env.example|Template]] |

---

## 📋 Metadata

```yaml
---
title: "Configuration Options Index"
type: index
category: configuration
audience: [devops, system-administrators]
status: production
version: 1.0.0
created: 2025-01-20
tags:
  - index
  - configuration
  - environment
  - variables
---
```

---

**Status**: Production-Ready ✓
