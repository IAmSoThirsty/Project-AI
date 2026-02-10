# H.323 Lifecycle & Decommissioning Standard

Version 1.0 — Deployment, Maintenance, Retirement

## 1. Purpose

Defines the full lifecycle of H.323 components from deployment to retirement, ensuring security and operational integrity throughout.

---

## 2. Lifecycle Phases

### 2.1 Deployment

**Certificate issuance**

- Request X.509 certificate from Voice/Video CA
- Install certificate on component
- Validate certificate chain
- Configure CRL/OCSP

**Secure configuration**

- Apply hardening baseline (see Hardening Checklist)
- Enable H.235.2/3/4/6
- Configure SRTP mandatory mode
- Lock admin interface
- Set strong passwords

**Baseline documentation**

- Record component details (model, serial, IP, MAC)
- Document configuration parameters
- Capture initial baseline config
- Add to asset inventory

**Monitoring integration**

- Configure syslog export to SIEM
- Enable SNMP monitoring
- Configure health check endpoints
- Create dashboard entries
- Enable alerting rules

### 2.2 Operation

**Daily/weekly/monthly maintenance**

- Daily: Health checks, registration validation
- Weekly: Certificate expiry checks, log review
- Monthly: Firmware review, PKI audit, capacity review

**PKI renewals**

- Certificate renewal 30 days before expiry
- CRL/OCSP availability validation
- Trust chain verification

**Firmware updates**

- Review security advisories
- Test updates in lab environment
- Schedule maintenance window
- Apply updates
- Validate secure operation post-update

**Capacity planning**

- Monitor call volume trends
- Review bandwidth utilization
- Plan gateway trunk expansion
- Plan endpoint additions

### 2.3 Decommissioning

**Revoke certificates**

- Submit revocation request to PKI team
- Validate certificate appears in CRL
- Confirm OCSP returns "revoked" status

**Wipe configuration**

- Factory reset device
- Overwrite flash/storage (DoD 5220.22-M standard)
- Validate no configuration remnants

**Remove from GK**

- Delete endpoint aliases from Gatekeeper
- Remove E.164 routing entries
- Remove from admission control policies

**Remove from monitoring**

- Delete SIEM log source
- Remove SNMP targets
- Delete dashboard entries
- Disable alerting rules

**Update diagrams and inventory**

- Remove component from network diagrams
- Update asset inventory
- Archive decommissioning documentation

---

## 3. Decommissioning Checklist

### 3.1 Pre-Decommissioning

- [ ] Change request approved
- [ ] Maintenance window scheduled
- [ ] Replacement component deployed (if applicable)
- [ ] Backup configuration captured
- [ ] Users notified

### 3.2 Decommissioning Steps

- [ ] **Certificate revoked** (PKI team confirms)
- [ ] **Device configuration backed up** (final backup)
- [ ] **Device unregistered from GK**
- [ ] **GK alias removed** (H.323 ID, E.164)
- [ ] **Device wiped** (factory reset + secure erase)
- [ ] **Firewall rules updated** (remove specific ACLs)
- [ ] **Monitoring disabled** (SIEM, SNMP, dashboards)
- [ ] **Asset inventory updated** (status: decommissioned)
- [ ] **Network diagrams updated**
- [ ] **Documentation archived** (config, logs, certificates)

### 3.3 Post-Decommissioning Validation

- [ ] Certificate confirmed in CRL
- [ ] No log traffic from decommissioned device
- [ ] No alerts referencing device
- [ ] Network scans show device offline
- [ ] Asset tracking updated

---

## 4. Lifecycle State Model

### 4.1 State Definitions

| State | Description | Actions Allowed |
|-------|-------------|-----------------|
| **Planned** | Component planned but not yet deployed | Procurement, design, documentation |
| **Deployed** | Component deployed but not yet operational | Configuration, testing, integration |
| **Operational** | Component in production use | Monitoring, maintenance, troubleshooting |
| **Maintenance** | Component temporarily offline for updates | Firmware updates, configuration changes, repair |
| **Deprecated** | Component scheduled for decommissioning | Migration planning, user notification |
| **Decommissioned** | Component retired and removed | Archival, disposal |

### 4.2 State Transitions

```
Planned → Deployed → Operational → Maintenance → Operational
                                  ↓
                              Deprecated → Decommissioned
```

---

## 5. Component-Specific Lifecycle Procedures

### 5.1 Endpoint Lifecycle

**Deployment**:

1. Issue certificate
1. Install certificate
1. Configure GK address
1. Enable H.235.2/3/4
1. Enable SRTP
1. Lock admin UI
1. Register with GK
1. Add to monitoring

**Operation**:

- Daily: Validate registration status
- Weekly: Check certificate expiry
- Monthly: Firmware review

**Decommissioning**:

1. Revoke certificate
1. Unregister from GK
1. Factory reset
1. Remove from inventory

### 5.2 Gatekeeper Lifecycle

**Deployment**:

1. Issue certificate
1. Install GK software/appliance
1. Configure H.235.2/3/4
1. Configure routing rules
1. Configure admission control
1. Enable logging to SIEM
1. Configure redundancy (active/standby)
1. Validate failover

**Operation**:

- Daily: Health check, registration counts
- Weekly: Log review, certificate check
- Monthly: Capacity review, PKI audit

**Decommissioning**:

1. Migrate endpoints to secondary GK
1. Validate no active registrations
1. Revoke certificate
1. Wipe configuration
1. Remove from monitoring
1. Update diagrams

### 5.3 Gateway Lifecycle

**Deployment**:

1. Issue certificate
1. Install gateway in DMZ
1. Configure trunks (PSTN/H.320/SIP)
1. Configure H.235.2/3/4/6
1. Configure codec mapping
1. Enable CDR export
1. Validate trunk status
1. Test call flows

**Operation**:

- Daily: Trunk status, active calls
- Weekly: CDR review, certificate check
- Monthly: Trunk utilization, firmware review

**Decommissioning**:

1. Migrate calls to secondary gateway
1. Validate no active calls
1. Disconnect trunks (coordinate with carrier)
1. Revoke certificate
1. Wipe configuration
1. Remove from monitoring
1. Update diagrams

---

## 6. Certificate Lifecycle Management

### 6.1 Certificate Issuance

- Request CSR from component
- Submit to Voice/Video CA
- Validate certificate fields (SAN, validity period)
- Install certificate
- Validate trust chain

### 6.2 Certificate Renewal

- **Trigger**: 30 days before expiry
- Generate new CSR
- Submit to CA
- Install new certificate
- Validate operation
- Revoke old certificate (after grace period)

### 6.3 Certificate Revocation

- **Triggers**: Component decommissioned, key compromise, policy violation
- Submit revocation request to PKI team
- Validate CRL updated within 4 hours
- Validate OCSP responds "revoked"
- Component fails authentication immediately

### 6.4 Certificate Expiry Monitoring

**Alerting Thresholds**:

- 30 days: WARN (schedule renewal)
- 14 days: ERROR (urgent renewal required)
- 7 days: CRITICAL (component will fail soon)
- 0 days: CRITICAL (component failing authentication)

---

## 7. Configuration Management

### 7.1 Baseline Configuration

- Capture initial configuration post-deployment
- Store in version control (Git)
- Tag with version number and date

### 7.2 Configuration Changes

- All changes via change control process
- Backup current configuration before change
- Apply change
- Validate operation
- Update baseline if change permanent

### 7.3 Configuration Backups

- **Frequency**: Daily (automated)
- **Retention**: 90 days
- **Location**: Secure backup storage
- **Encryption**: AES-256

### 7.4 Configuration Drift Detection

- Automated comparison vs. baseline
- Alert on unauthorized changes
- Investigate and remediate drift

---

## 8. Firmware & Software Lifecycle

### 8.1 Firmware Review Cycle

- **Monthly**: Check vendor security advisories
- **Quarterly**: Review firmware versions vs. latest
- **Annually**: Mandatory firmware update cycle

### 8.2 Firmware Update Process

1. Review release notes
1. Test in lab environment
1. Schedule maintenance window
1. Backup current configuration
1. Apply firmware update
1. Validate operation (registration, secure call setup, SRTP)
1. Monitor for 48 hours
1. Document results

### 8.3 Firmware Rollback

- **Trigger**: Update causes operational failure
- Restore previous firmware version
- Restore configuration backup
- Validate operation
- Report issue to vendor

---

## 9. Disposal & Data Sanitization

### 9.1 Data Sanitization Requirements

- **Level 1** (low sensitivity): Single-pass overwrite
- **Level 2** (medium sensitivity): DoD 5220.22-M (3-pass)
- **Level 3** (high sensitivity): DoD 5220.22-M (7-pass) + physical destruction

### 9.2 H.323 Component Disposal

**All components**: Minimum Level 2 (DoD 5220.22-M)

**Process**:

1. Revoke certificates
1. Factory reset
1. Secure erase (3-pass minimum)
1. Validate no data recoverable
1. Physical disposal or redeployment

### 9.3 Certificate & Key Material Disposal

- Delete private keys
- Overwrite key storage (secure erase)
- Revoke certificates
- Confirm keys unrecoverable

---

## 10. Lifecycle Documentation Requirements

### 10.1 Deployment Documentation

- Asset tag and serial number
- Certificate serial number
- Initial configuration
- Deployment date and engineer
- Baseline test results

### 10.2 Operational Documentation

- Change history
- Incident history
- Firmware update history
- Certificate renewal history
- Performance metrics

### 10.3 Decommissioning Documentation

- Decommissioning date and engineer
- Reason for decommissioning
- Certificate revocation confirmation
- Data sanitization confirmation
- Disposal method

---

## 11. Lifecycle Audit Requirements

### 11.1 Quarterly Lifecycle Audit

- [ ] All components in inventory have valid certificates
- [ ] All components registered in monitoring
- [ ] All baselines current (< 90 days old)
- [ ] All decommissioned components removed from GK
- [ ] All decommissioned components wiped

### 11.2 Annual Lifecycle Audit

- [ ] Full inventory reconciliation
- [ ] Firmware versions compliant
- [ ] Certificate lifecycle compliance
- [ ] Configuration drift remediated
- [ ] Decommissioning procedures validated

---

## 12. Completion Criteria

A component lifecycle is considered compliant when:

- All phases documented
- Certificates managed throughout lifecycle
- Configurations backed up regularly
- Monitoring active during operational phase
- Decommissioning procedure followed
- Data sanitization validated
- Asset inventory updated
