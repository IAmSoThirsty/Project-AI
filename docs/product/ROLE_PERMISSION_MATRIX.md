# Human Interface Role and Permission Matrix

**Status:** Implemented for current account, evidence, request, review, SWR execution,
and Atlas replay APIs; later module actions still require their own denial tests.

Human-interface roles decide which product surfaces a person may use. They never
grant capabilities, governance verdicts, or execution authority. Every consequential
request must still cross the canonical identity, capability, governance, audit, and
execution boundaries.

| Surface / action | Owner | Administrator | Operator | Reviewer | Auditor | Viewer |
|---|---:|---:|---:|---:|---:|---:|
| View Command Center | Yes | Yes | Yes | Yes | Yes | Yes |
| View evidence and verified audit records | Yes | Yes | Yes | Yes | Yes | Yes |
| Manage own password and sessions | Yes | Yes | Yes | Yes | Yes | Yes |
| Create or deactivate human accounts | Yes | Yes | No | No | No | No |
| Assign interface roles | Yes | Yes, except Owner | No | No | No | No |
| Revoke another user's sessions | Yes | Yes, except Owner | No | No | No | No |
| Submit an execution request | Yes | Yes | Yes | No | No | No |
| Review assigned requests | Yes | Yes | No | Yes | No | No |
| Run bounded Atlas replay analysis | Yes | Yes | Yes | Yes | Yes | No |
| Initiate reviewed module execution | Yes | Yes | Yes | No | No | No |
| Export audit evidence | Yes | Yes | No | Yes | Yes | No |
| Configure deployment/security policy | Yes | Yes, except Owner transfer | No | No | No | No |

## Enforcement status

- Implemented: exactly-once Owner bootstrap, managed account creation, role assignment,
  activation/deactivation, forced first password change, session revocation, and an
  administration screen.
- Implemented: server-side permission checks for evidence access, account/role/security
  event administration, request submission, request review, Atlas replay analysis, and
  SWR execution initiation.
- Implemented: self-review denial and recent MFA step-up for review decisions.
- Implemented: versioned governed-request input schemas and a dedicated
  `modules.analysis.run` permission that denies Viewer replay attempts server-side.
- Not implemented: custom roles, Owner transfer, or module-specific actions beyond the
  current Atlas and SWR contracts. Audit export is bounded to the verified displayed page.
- Required before additional roles are enabled: server-side permission checks and a
  deterministic denial test for every protected action. Hiding a control is not
  authorization.
