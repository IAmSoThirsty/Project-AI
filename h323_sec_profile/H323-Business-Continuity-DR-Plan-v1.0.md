# H.323 Business Continuity & Disaster Recovery Plan

Version 1.0 — High Availability & Failover Strategy

## 1. Purpose

Defines how to maintain secure H.323 operations during outages, disasters, or infrastructure failures.

---

## 2. High Availability Architecture

### 2.1 Gatekeeper HA

**Active/Standby Configuration**:

- Primary GK: Active, handling all registrations
- Secondary GK: Standby, synchronized database
- Automatic failover: < 30 seconds
- Shared database: PostgreSQL replication or shared SAN

**Cluster Configuration** (Alternative):

- Multiple GKs in active-active cluster
- Load balanced via DNS or hardware LB
- Shared state via distributed database
- Higher complexity, higher availability

**Failover Triggers**:

- Primary GK process failure
- Network partition
- Hardware failure
- Manual failover (maintenance)

**Failover Procedure**:

1. Monitor detects primary GK failure
1. Secondary GK promoted to active
1. Endpoints re-register (automatic via GRQ)
1. Calls reroute through secondary GK
1. Alert sent to operations team

### 2.2 Gateway HA

**N+1 Redundancy**:

- Primary gateway: Active calls
- Backup gateway: Hot standby
- Automatic rerouting on failure
- Load balancing for high call volume

**Trunk Failover**:

- Primary PSTN trunk fails
- Calls reroute to secondary trunk
- Carrier coordination required

**Load Balancing**:

- Round-robin across multiple gateways
- Least-loaded gateway selection
- GK-controlled routing

### 2.3 Network HA

**Redundant Paths**:

- Dual core switches (HSRP/VRRP)
- Redundant WAN links (MPLS + Internet VPN)
- Redundant firewalls (active/standby or active/active)

**Redundant NTP**:

- Primary NTP server: stratum 1 or 2
- Secondary NTP servers: Multiple sources
- Fallback: GPS-based NTP appliance

**Redundant PKI**:

- Multiple OCSP responders
- CRL mirroring across data centers
- Cached CRLs on endpoints (7-day validity)

---

## 3. Disaster Recovery Scenarios

### 3.1 Gatekeeper Failure

**Scenario**: Primary GK suffers hardware failure

**Detection**:

- Health check fails (< 10 seconds)
- Endpoints unable to register
- RAS port unreachable

**Recovery Steps**:

1. Secondary GK detects primary failure (heartbeat timeout)
1. Secondary GK assumes active role
1. Endpoints send GRQ (Gatekeeper Request)
1. Secondary GK responds with GCF (Gatekeeper Confirm)
1. Endpoints re-register (RRQ/RCF)
1. Operations team notified
1. Primary GK repaired/replaced
1. Primary GK brought online as standby

**Expected Downtime**: < 30 seconds

### 3.2 Gateway Failure

**Scenario**: Primary gateway fails during active calls

**Detection**:

- Gateway heartbeat fails
- Active calls drop
- Trunk status down

**Recovery Steps**:

1. GK detects gateway failure (ARQ timeout or trunk down)
1. GK marks gateway as unavailable
1. New calls reroute to secondary gateway
1. Active calls drop (cannot be recovered mid-call)
1. Users redial, connect via secondary gateway
1. Operations team notified
1. Primary gateway repaired
1. Primary gateway restored to service

**Expected Downtime**: Active calls lost, new calls immediate

### 3.3 Network Partition

**Scenario**: WAN link between Site A and Site B fails

**Detection**:

- LRQ/LCF timeout
- Routing failures
- Network monitoring alert

**Local Survivability Mode**:

1. Site B GK detects Site A GK unreachable
1. Site B endpoints remain registered locally
1. Local calls within Site B continue
1. External calls route via Site B gateway (local PSTN)
1. Inter-site calls temporarily unavailable

**Recovery Steps**:

1. WAN link restored
1. GK-to-GK communication reestablished
1. Routing tables synchronized
1. Inter-site calls resume

**Expected Downtime**: Inter-site calls only, local calls unaffected

### 3.4 PKI Outage

**Scenario**: CRL/OCSP servers unreachable

**Detection**:

- Certificate validation failures
- OCSP timeout
- CRL fetch failure

**Cached CRL Fallback**:

1. Endpoints use cached CRLs (up to 7 days old)
1. OCSP stapling (if configured) continues
1. Certificate validation proceeds with cached data
1. Security posture maintained (fail-secure)

**Recovery Steps**:

1. Restore CRL/OCSP availability
1. Endpoints fetch fresh CRLs
1. OCSP queries resume
1. Operations team validates no revoked certs accepted during outage

**Expected Downtime**: None (cached CRLs provide continuity)

### 3.5 Data Center Failure

**Scenario**: Primary data center suffers complete outage (fire, flood, power)

**Detection**:

- All components unreachable
- Network monitoring alerts
- Physical security alerts

**Recovery Steps**:

1. Activate DR site (secondary data center)
1. Failover DNS to DR site IPs
1. Endpoints re-register to DR GKs
1. Gateways connect to DR PSTN trunks
1. Operations team relocates to DR site (if necessary)
1. Validate all services operational
1. Primary site repaired
1. Failback to primary site (planned maintenance)

**Expected Downtime**: 15-60 minutes (depends on automation level)

---

## 4. DR Testing Requirements

### 4.1 Quarterly Failover Tests

**Gatekeeper Failover Test**:

- Simulate primary GK failure (shutdown service)
- Validate endpoints re-register to secondary
- Validate call routing through secondary
- Measure failover time
- Restore primary GK

**Gateway Failover Test**:

- Simulate primary gateway failure (disconnect trunk)
- Validate calls reroute to secondary gateway
- Validate SRTP maintained
- Measure reroute time
- Restore primary gateway

**Network Failover Test**:

- Simulate WAN link failure
- Validate local survivability
- Validate local calls continue
- Restore WAN link

**Expected Results**:

- GK failover < 30 seconds
- Gateway reroute immediate
- Local survivability functional

### 4.2 Annual Full DR Simulation

**Scenario**: Primary data center failure

**Test Procedure**:

1. Schedule maintenance window
1. Shut down primary data center (simulated)
1. Activate DR site
1. Failover DNS
1. Validate endpoint registration
1. Validate call routing
1. Validate SRTP enforcement
1. Validate logging to SIEM
1. Measure failover time
1. Restore primary site
1. Failback to primary
1. Document results

**Success Criteria**:

- All endpoints register within 5 minutes
- All calls route successfully
- All security controls enforced
- All logs captured
- Failover time < 60 minutes

### 4.3 DR Test Documentation

**Required Documentation**:

- Test date and participants
- Test scenario
- Test results (pass/fail)
- Failover time measurements
- Issues encountered
- Remediation actions
- Lessons learned

---

## 5. Recovery Time Objectives (RTO) & Recovery Point Objectives (RPO)

### 5.1 RTO Targets

| Component | RTO | Notes |
|-----------|-----|-------|
| Gatekeeper | 30 seconds | Automatic failover |
| Gateway | Immediate (new calls) | Active calls lost |
| Endpoint | 2 minutes | Re-registration time |
| Network | 30 seconds | HSRP/VRRP failover |
| PKI | 0 (cached CRLs) | Cached for 7 days |
| Data Center | 60 minutes | Full DR site activation |

### 5.2 RPO Targets

| Data Type | RPO | Backup Frequency |
|-----------|-----|------------------|
| GK registrations | 0 (real-time sync) | Continuous replication |
| Gateway configuration | 24 hours | Daily backup |
| Endpoint configuration | 24 hours | Daily backup |
| Call logs (CDRs) | 0 (real-time) | SIEM streaming |
| PKI certificates | N/A | Not applicable (distributed) |

---

## 6. Backup & Restore Procedures

### 6.1 Gatekeeper Backup

**Daily Backup**:
```bash

#!/bin/bash

# Backup GK configuration and database

gk-backup --config /etc/gk/config.xml --output /backup/gk-$(date +%Y%m%d).tar.gz
pg_dump h323_db > /backup/gk-db-$(date +%Y%m%d).sql
```

**Restore Procedure**:
```bash

# Restore GK configuration

tar -xzf /backup/gk-20260123.tar.gz -C /etc/gk/

# Restore database

psql h323_db < /backup/gk-db-20260123.sql

# Restart GK

systemctl restart gatekeeper
```

### 6.2 Gateway Backup

**Daily Backup**:
```bash

# Export gateway configuration

gateway-cli export-config > /backup/gw-$(date +%Y%m%d).xml
```

**Restore Procedure**:
```bash

# Import gateway configuration

gateway-cli import-config /backup/gw-20260123.xml

# Restart gateway

systemctl restart gateway
```

### 6.3 Backup Retention

| Backup Type | Retention | Storage Location |
|-------------|-----------|------------------|
| Daily | 30 days | On-site backup storage |
| Weekly | 90 days | On-site + off-site |
| Monthly | 1 year | Off-site only |
| Annual | 7 years | Archive storage |

---

## 7. Communication Plan

### 7.1 Incident Notification

**Immediate Notification** (within 5 minutes):

- NOC team
- SOC team
- Voice/Video engineering lead

**Escalation** (within 15 minutes):

- IT management
- Business stakeholders (if user-impacting)

**User Communication** (within 30 minutes):

- Internal announcement (email, Slack)
- Status page update

### 7.2 Incident Status Updates

**Frequency**:

- Every 30 minutes during incident
- Final update upon resolution

**Content**:

- Current status
- Impact assessment
- Estimated time to resolution
- Workarounds (if available)

---

## 8. Disaster Recovery Site Requirements

### 8.1 Infrastructure

**DR Site Must Have**:

- Redundant power (UPS + generator)
- Redundant network connectivity
- Sufficient rack space
- Environmental controls (HVAC)

**DR Equipment**:

- Standby Gatekeeper servers
- Standby Gateway appliances
- Standby firewalls
- Standby switches/routers

### 8.2 Data Synchronization

**Real-Time Sync**:

- GK registration database (PostgreSQL replication)
- PKI CRLs (rsync every 4 hours)

**Daily Sync**:

- Configuration backups
- CDR archives

### 8.3 Network Connectivity

**DR Site WAN**:

- Dedicated WAN link to primary site (MPLS)
- Internet backup (VPN)
- PSTN trunks to local carrier

---

## 9. Business Continuity Playbook

### 9.1 Minor Outage (Single Component)

**Response**:

1. Automatic failover (if configured)
1. Or manual failover by operations
1. Monitor for stability
1. Schedule repair during next maintenance window

### 9.2 Major Outage (Multiple Components)

**Response**:

1. Activate incident response team
1. Assess scope and impact
1. Prioritize critical services
1. Execute recovery procedures
1. Communicate with stakeholders
1. Post-incident review

### 9.3 Catastrophic Outage (Data Center Loss)

**Response**:

1. Declare disaster
1. Activate DR site
1. Failover all services
1. Notify all users
1. Operate from DR site until primary restored
1. Plan failback to primary

---

## 10. Completion Criteria

Business continuity and DR plans are considered compliant when:

- All redundancy validated (GK, GW, network)
- All failover procedures tested quarterly
- Full DR simulation tested annually
- RTO/RPO targets met
- Backup/restore procedures validated
- Communication plan documented
- DR site maintained and ready
- All documentation current
