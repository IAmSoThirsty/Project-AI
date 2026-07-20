# Communications and Support Plan — Successor to v0.0.2

**Status:** Message content drafted; recipients, channels, owners, and times
pending.

## Contact and channel record

| Role/channel | Required value |
|---|---|
| Change owner | TBD |
| Implementer | TBD |
| Rollback owner / backup | TBD / TBD |
| Support owner/on-call rota | TBD |
| Security escalation | TBD |
| Data/storage escalation | TBD |
| Stakeholder distribution | TBD |
| Change coordination channel | TBD |
| Incident channel/bridge | TBD |
| User-facing status channel | TBD or explicitly not applicable |

## Communication timeline

| Timing | Message/action | Owner |
|---|---|---|
| At CAB approval | Record scope, conditions, window, owners, and rollback revision | Change owner |
| 24h before | Stakeholder/support notice and reminder of escalation route | Communications owner TBD |
| 30m before | Confirm go/no-go, freeze status, staffing, backups, dashboards, and change channel | Change owner |
| Change start | Announce start, candidate commit/tag, expected impact, next update | Implementer |
| Every 15m | Status, health, risks, incidents, next checkpoint | Implementer/support |
| Rollback trigger | Declare incident/rollback, impact, owner, next update time | Incident commander |
| Change complete | Report validation, observation start, remaining watch items | Change owner |
| Observation exit | Report success or rollback, exact revision/digests, acceptance, follow-up | Change owner |

## Stakeholder notice draft

**Subject:** Planned Project-AI `<APPROVED_VERSION>` change — `<WINDOW AND TIMEZONE>`

Project-AI `<APPROVED_VERSION>` is proposed for deployment to `<ENVIRONMENT/CLUSTER>` in
namespace `<NAMESPACE>` during `<START–END, TIMEZONE>`. The change updates the
API, three portals, SWR, Atlas, Arbiter/RLP, and Genesis container workloads.
Expected impact is `<TBD AFTER TARGET INSPECTION>`.

The implementation owner is `<NAME>`, rollback owner is `<NAME>`, and support
owner is `<NAME/ROTA>`. Status will be posted in `<CHANNEL>`. Report impact or
unexpected behavior through `<SUPPORT ROUTE>`. The recovery plan is Helm
rollback to certified revision `<REVISION/TAG>`; deployment will stop if health,
authorization, audit integrity, or agreed performance checks fail.

## Change-start draft

Starting Project-AI `<APPROVED_VERSION>` change `<CHANGE ID>` now. Candidate commit:
`<APPROVED_COMMIT>`; target:
`<CONTEXT>/<NAMESPACE>`; expected completion: `<TIME>`. Next update in 15
minutes. Escalation: `<ROUTE>`.

## Completion draft

Project-AI change `<CHANGE ID>` completed at `<TIME>`. Active Helm revision:
`<REVISION>`; image digests: `<EVIDENCE LINK>`. Health, protected-route,
governance denial, audit-chain, persistence, metrics, and alert-delivery checks
`<PASSED/FAILED WITH DETAILS>`. Observation continues until `<TIME>`. Remaining
issues: `<NONE OR LIST>`. Acceptance owner: `<NAME>`.

## Rollback/incident draft

Project-AI change `<CHANGE ID>` entered rollback at `<TIME>` because
`<TRIGGER>`. Current impact: `<IMPACT>`. Rollback owner: `<NAME>`. Target
revision: `<REVISION/TAG/DIGEST>`. Next update at `<TIME>`. Incident route:
`<CHANNEL/BRIDGE>`.

## Support briefing

Support must receive, before the window:

- release scope and expected impact;
- health/status locations and known limitations;
- authentication and authorization symptoms that require immediate escalation;
- audit-integrity and data/persistence escalation criteria;
- named implementation, rollback, security, and data owners;
- user-safe status language and prohibited disclosure of credentials/secrets;
- rollback trigger list and update cadence.

No claim of “no customer impact” is authorized until the target and traffic are
inspected and the change authority approves that statement.
