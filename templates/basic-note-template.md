---
title: "<% tp.file.title %>"
created: <% tp.file.creation_date("YYYY-MM-DD HH:mm") %>
modified: <% tp.file.last_modified_date("YYYY-MM-DD HH:mm") %>
tags: [sample, templater]
author: <% tp.user.name || "Project-AI" %>
status: draft
---

# <% tp.file.title %>

## 📋 Overview

<% tp.system.prompt("Brief description") %>

## 🎯 Objectives

- [ ] Objective 1
- [ ] Objective 2
- [ ] Objective 3

## 📝 Content

### Section 1

Content goes here...

### Section 2

More content...

## 🔗 Related Documents

- [[]]
- [[]]

## 📊 Metadata

| Property | Value |
|----------|-------|
| Created | <% tp.file.creation_date("YYYY-MM-DD") %> |
| Modified | <% tp.file.last_modified_date("YYYY-MM-DD") %> |
| File Path | <% tp.file.path() %> |
| Folder | <% tp.file.folder() %> |

---

**Last Updated:** <% tp.date.now("YYYY-MM-DD HH:mm:ss") %>
