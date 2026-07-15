# Inter-Skill Handoff Schema

Use this compact structure when another skill will consume the result:

```yaml
skill: <name>
status: complete|partial|blocked
scope: <resolved scope>
governing_version: thirsty-constitution-v0.1
sources:
  - id: <stable source identifier>
    version: <version/date/commit when known>
claims:
  - statement: <claim>
    epistemic_status: observed|verified|reported|inferred|hypothesized|normative|contested|unknown
    source_ids: []
assumptions: []
contradictions: []
risks: []
irreversible_effects: []
unresolved_questions: []
recommended_next_skills: []
external_actions_taken: []
```

Never populate `external_actions_taken` with an action that was not actually performed.
