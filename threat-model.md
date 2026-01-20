# Threat Model (initial)

## Attacker capabilities
- Remote user submitting crafted prompts and inputs.
- Supply chain attacks via malicious dependencies.

## Trust boundaries
- User input vs. model output
- Inter-process communication and plugin interfaces

## Mitigations
- Input validation and sanitization
- Rate limiting and guard agents (Cerberus)
- Audit logging for critical operations
- Secrets not committed to repo (.env excluded)

## Next steps
- Formalize per-source rate limiting with Redis
- Add fuzz tests for prompt injection
