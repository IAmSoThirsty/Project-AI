---
created: <% tp.file.creation_date("YYYY-MM-DD") %>
updated: <% tp.file.last_modified_date("YYYY-MM-DD") %>
type: research-paper-notes
category: research
status: reading
paper_title: <% tp.system.prompt("Paper title", "") %>
authors: []
publication_year: <% tp.system.prompt("Publication year", new Date().getFullYear().toString()) %>
publication_venue: <% tp.system.prompt("Conference/Journal", "") %>
doi: <% tp.system.prompt("DOI (optional)", "") %>
arxiv_id: <% tp.system.prompt("arXiv ID (optional)", "") %>
citation_count: <% tp.system.prompt("Citation count (optional)", "") %>
read_date: <% tp.file.creation_date("YYYY-MM-DD") %>
reading_status: not-started
relevance: <% tp.system.prompt("Relevance to work (High/Medium/Low)", "Medium") %>
tags: [research, paper, literature]
aliases: []
---

# 📄 <%* tR += tp.frontmatter.paper_title %>

## Paper Metadata

| Field | Value |
|-------|-------|
| **Authors** | <% tp.system.prompt("Authors (comma-separated)", "") %> |
| **Year** | <% tp.frontmatter.publication_year %> |
| **Venue** | <% tp.frontmatter.publication_venue %> |
| **Type** | Conference | Journal | Preprint | Workshop | Book Chapter |
| **DOI** | <% tp.frontmatter.doi %> |
| **arXiv** | <% tp.frontmatter.arxiv_id %> |
| **Citations** | <% tp.frontmatter.citation_count %> |
| **Read Date** | <% tp.frontmatter.read_date %> |

### Links

**Paper URL:** 

**PDF Link:** 

**Code Repository:** 

**Project Page:** 

**Related Resources:**
- 
- 

---

## Quick Summary

### One-Sentence Summary

> 

### Three-Sentence Summary

> 

### Keywords

<% tp.system.prompt("Keywords (comma-separated)", "") %>

### Research Area

- [ ] Machine Learning
- [ ] Deep Learning
- [ ] NLP
- [ ] Computer Vision
- [ ] Robotics
- [ ] Systems
- [ ] Theory
- [ ] HCI
- [ ] Security
- [ ] Other: _______________

---

## Reading Status

**Current Status:**
- [ ] 📋 Not Started
- [ ] 📖 Reading
- [ ] ✅ Completed
- [ ] 🔁 Re-reading
- [ ] ⏸️ Paused

**Reading Progress:** ____%

**Priority:**
- [ ] Must read (directly applicable)
- [ ] Should read (highly relevant)
- [ ] Nice to read (background knowledge)
- [ ] Low priority (tangential)

**Estimated Reading Time:** <% tp.system.prompt("Est. reading time (hours)", "2") %> hours
**Actual Reading Time:** _____ hours

---

## Research Context

### Problem Statement

**What problem does this paper address?**


**Why is this problem important?**


**What are the limitations of existing approaches?**


### Research Questions

1. 
2. 
3. 

### Hypotheses

1. 
2. 

---

## Main Contributions

<%* const numContributions = parseInt(tp.system.prompt("Number of main contributions", "3")); %>
<%* for (let i = 1; i <= numContributions; i++) { %>
### Contribution <%* tR += i %>: <% tp.system.prompt(`Contribution ${i} title`, "") %>

**Description:**


**Novelty:**


**Impact:**


---
<%* } %>

---

## Methodology

### Approach Overview

**High-level approach:**


**Key innovation:**


### Research Design

**Type:**
- [ ] Theoretical
- [ ] Empirical
- [ ] Experimental
- [ ] Survey/Review
- [ ] Case Study
- [ ] Mixed Methods

**Methods Used:**
- [ ] Algorithm/Model Development
- [ ] Experimental Evaluation
- [ ] User Study
- [ ] Simulation
- [ ] Formal Analysis
- [ ] Literature Review
- [ ] Other: _______________

### Technical Details

#### Model/Algorithm

**Architecture:**


**Key Components:**
1. 
2. 
3. 

**Formulation:**

```
[Mathematical formulation if applicable]
```

**Training Process:**


**Hyperparameters:**


#### Datasets

| Dataset | Size | Domain | Usage |
|---------|------|--------|-------|
| | | | Training |
| | | | Validation |
| | | | Testing |

#### Experimental Setup

**Hardware:**
- 

**Software/Frameworks:**
- 

**Computational Requirements:**
- 

**Reproducibility:**
- [ ] Code available
- [ ] Data available
- [ ] Detailed hyperparameters provided
- [ ] Random seeds specified

---

## Results

### Main Findings

<%* const numFindings = parseInt(tp.system.prompt("Number of main findings", "3")); %>
<%* for (let i = 1; i <= numFindings; i++) { %>
#### Finding <%* tR += i %>: <% tp.system.prompt(`Finding ${i} summary`, "") %>

**Evidence:**


**Statistical Significance:**


**Effect Size:**


---
<%* } %>

### Performance Metrics

| Metric | Baseline | Proposed Method | Improvement | Significance |
|--------|----------|-----------------|-------------|--------------|
| | | | | p < 0.05 |
| | | | | |
| | | | | |

### Comparison with Prior Work

| Method | Year | Metric 1 | Metric 2 | Advantages | Disadvantages |
|--------|------|----------|----------|------------|---------------|
| Proposed | <% tp.frontmatter.publication_year %> | | | | |
| Baseline 1 | | | | | |
| Baseline 2 | | | | | |

### Ablation Studies

**Component Removed** → **Impact:**
- 
- 
- 

### Visualizations

**Key Figures:**
- Figure 1: 
- Figure 2: 
- Figure 3: 

**Tables:**
- Table 1: 
- Table 2: 

---

## Strengths

### Technical Strengths

1. ✅ 
2. ✅ 
3. ✅ 

### Methodological Strengths

1. ✅ 
2. ✅ 

### Presentation Strengths

1. ✅ 
2. ✅ 

---

## Weaknesses & Limitations

### Technical Weaknesses

1. ⚠️ 
2. ⚠️ 
3. ⚠️ 

### Methodological Limitations

1. ⚠️ 
2. ⚠️ 

### Scope Limitations

**Assumptions:**
- 

**Generalizability:**
- 

**Unaddressed Issues:**
- 

---

## Critical Analysis

### Validity of Claims

**Are the claims well-supported?**


**Are there any overclaims?**


**What evidence is missing?**


### Experimental Rigor

**Strengths:**
- 

**Weaknesses:**
- 

**Suggestions for Improvement:**
- 

### Alternative Explanations

**Could the results be explained differently?**


**What confounding factors might exist?**


---

## Relevance to My Work

### Applicability

**How does this relate to my research?**


**Can I apply these methods/ideas?**


**Priority:** High | Medium | Low

### Potential Applications

1. 
2. 
3. 

### Ideas Sparked

**New Research Directions:**
- 
- 

**Extensions/Improvements:**
- 
- 

**Combinations with Other Work:**
- 
- 

---

## Key Takeaways

### Top 3 Insights

1. 💡 
2. 💡 
3. 💡 

### Actionable Items

- [ ] Try method X in my project
- [ ] Investigate dataset Y
- [ ] Read follow-up paper Z
- [ ] Implement technique W
- [ ] Contact authors about X

### Quotable Passages

> "_[Quote 1]_" (p. ___)

> "_[Quote 2]_" (p. ___)

---

## Related Work

### Prior Work (Background)

| Paper | Year | Relation | Notes |
|-------|------|----------|-------|
| | | Builds on this | |
| | | Extends this | |
| | | Inspired by this | |

### Concurrent Work

| Paper | Year | Relation | Comparison |
|-------|------|----------|------------|
| | | Similar approach | |
| | | Alternative method | |

### Follow-up Work

| Paper | Year | Relation | Key Advancement |
|-------|------|----------|-----------------|
| | | Extends this paper | |
| | | Applies this work | |
| | | Critiques this paper | |

### Papers to Read Next

1. 📚 **[Paper Title]** - Why: 
2. 📚 **[Paper Title]** - Why: 
3. 📚 **[Paper Title]** - Why: 

---

## Implementation Notes

### Reproduction Attempts

**Status:**
- [ ] Not attempted
- [ ] In progress
- [ ] Successful
- [ ] Failed

**Notes:**


**Challenges:**
- 

**Code/Resources:**
- 

### Modifications/Extensions

**Ideas to try:**
1. 
2. 
3. 

**Expected Improvements:**
- 

---

## Discussion Points

### Questions for Authors

1. ❓ 
2. ❓ 
3. ❓ 

### Unclear Aspects

1. 🤔 
2. 🤔 

### Contradictions or Puzzles

1. 
2. 

---

## Citation Information

### BibTeX

```bibtex
@<% tp.system.prompt("Publication type (article/inproceedings/misc)", "article") %>{<% tp.system.prompt("Citation key", "author2026paper") %>,
  title={<% tp.frontmatter.paper_title %>},
  author={<% tp.system.prompt("Authors for BibTeX", "") %>},
  journal={<% tp.frontmatter.publication_venue %>},
  year={<% tp.frontmatter.publication_year %>},
  doi={<% tp.frontmatter.doi %>}
}
```

### Plain Text Citation

<% tp.system.prompt("Authors (last names)", "") %> et al. "<% tp.frontmatter.paper_title %>." _<% tp.frontmatter.publication_venue %>_, <% tp.frontmatter.publication_year %>.

---

## Connections

### Related Papers in Vault

```dataview
TABLE type as Type, publication_year as Year, relevance as Relevance
FROM ""
WHERE type = "research-paper-notes" AND file.name != this.file.name
SORT publication_year DESC
LIMIT 10
```

### Related Projects

- 
- 

### Relevant Techniques/Concepts

- [[Technique 1]]
- [[Concept 1]]
- [[Method 1]]

---

## Reading Notes

### Abstract Notes



### Introduction Notes



### Section-by-Section Notes

#### Section 2: 



#### Section 3: 



#### Section 4: 



#### Section 5: 



### Conclusion Notes



---

## Review & Rating

### Overall Rating

**Technical Quality:** ⭐⭐⭐⭐⭐ (1-5)
**Novelty:** ⭐⭐⭐⭐⭐ (1-5)
**Impact:** ⭐⭐⭐⭐⭐ (1-5)
**Clarity:** ⭐⭐⭐⭐⭐ (1-5)
**Reproducibility:** ⭐⭐⭐⭐⭐ (1-5)

**Overall Score:** ___/25

### Recommendation

**If I were a reviewer:**
- [ ] Strong Accept
- [ ] Accept
- [ ] Weak Accept
- [ ] Borderline
- [ ] Weak Reject
- [ ] Reject
- [ ] Strong Reject

**Confidence Level:** High | Medium | Low

**Review Summary:**


---

## Follow-up Actions

- [ ] Add to reading list: [[Reading List]]
- [ ] Discuss in group meeting
- [ ] Cite in my paper
- [ ] Implement method
- [ ] Run experiments
- [ ] Contact authors
- [ ] Present in journal club
- [ ] Write blog post summary

**Next Review Date:** <% tp.system.prompt("Next review date (optional)", "") %>

---

## Tags & Organization

**Topics:** #<% tp.system.prompt("Topic tags (space-separated)", "machine-learning") %>

**Methods:** #<% tp.system.prompt("Method tags (space-separated)", "") %>

**Domain:** #<% tp.system.prompt("Domain tag", "nlp") %>

**Collection:** 
- [ ] Core reading list
- [ ] Background reading
- [ ] Related work for paper X
- [ ] Survey/Review material

---

## Metadata

**Notes Created:** <% tp.file.creation_date("YYYY-MM-DD") %>
**Last Updated:** <% tp.file.last_modified_date("YYYY-MM-DD") %>
**Version:** 1.0

**Read by:** <% tp.system.prompt("Your name", "") %>
**Review Status:** Draft | In Review | Final

---

> **Reading Strategy:** Skim → Key sections → Full read → Critical analysis → Implementation
> **Time Investment:** Reading + Notes + Analysis = Total learning time

<!-- sovereign-vault-index-link -->
Central Index: [[Sovereign Vault Index]]

