# Contrarian Firewall - Operations Runbook

## God-Tier Operations Guide

Quick reference for deploying, monitoring, and maintaining the Contrarian Firewall.

---

## Quick Start

```bash
# Start server (orchestrator auto-starts)
uvicorn api.main:app --host 0.0.0.0 --port 8000

# Activate chaos engine
curl -X POST http://localhost:8000/api/firewall/chaos/start

# Check status
curl http://localhost:8000/api/firewall/status | jq '.'
```

---

## Key Operations

### Monitor Threats
```bash
# Threat score
curl http://localhost:8000/api/firewall/threat/score

# Cognitive warfare status
curl http://localhost:8000/api/firewall/cognitive/overload

# Comprehensive status
curl http://localhost:8000/api/firewall/status
```

### Report Violations
```bash
curl -X POST http://localhost:8000/api/firewall/violation/detect \
  -H "Content-Type: application/json" \
  -d '{
    "source_ip": "192.168.1.100",
    "violation_type": "sql_injection",
    "details": {"payload": "malicious"}
  }'
```

### Tune Parameters
```bash
curl -X POST http://localhost:8000/api/firewall/chaos/tune \
  -H "Content-Type: application/json" \
  -d '{
    "base_decoy_count": 20,
    "swarm_multiplier": 4.0,
    "auto_tune_enabled": true
  }'
```

---

## Alert Thresholds

| Metric | Normal | Warning | Critical |
|--------|--------|---------|----------|
| Threat Score | 0-30 | 31-60 | 61-100 |
| Cognitive Overload | 5-8.5 | <5 or >9 | >9.5 |
| Swarm Active | false | - | true |
| Violations/min | <10 | 10-50 | >50 |

---

## Incident Response

### SWARM Level Attack
1. Verify legitimacy
2. Check cognitive overload
3. Review intent history
4. Engage security team if real

### High False Positives
1. Reduce chaos multiplier
2. Increase escalation threshold
3. Review policy rules

### Performance Issues
1. Disable governance temporarily
2. Reduce telemetry frequency
3. Scale horizontally

---

## Maintenance

**Daily:**
- Check health endpoint
- Review threat trends

**Weekly:**
- Export telemetry
- Review intent history
- Rotate adversary profiles

**Monthly:**
- Performance benchmarking
- Security audit
- Documentation updates

---

## Resources

- [Architecture Documentation](../architecture/CONTRARIAN_FIREWALL_ARCHITECTURE.md)
- [API Integration Guide](../developer/CONTRARIAN_FIREWALL_API_GUIDE.md)
- [Test Suite](../../tests/test_contrarian_firewall.py)

---

**Operated with God-tier excellence.** 🛡️⚡
