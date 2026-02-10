# H.323 Configuration Baselines

Version 1.0 — Standardized Secure Configurations (GK, GW, EP)

## 1. Purpose

Defines standardized, secure configuration baselines for all H.323 components to ensure consistent security posture, operational reliability, and compliance across the enterprise.

---

## 2. Gatekeeper Baseline Configuration

### 2.1 Security Configuration

**H.235 Profiles**:
```xml
<h235-config>
  <profile name="H.235.2" enabled="true" mandatory="true"/>
  <profile name="H.235.3" enabled="true" mandatory="true"/>
  <profile name="H.235.4" enabled="true" mandatory="true"/>
  <anti-replay enabled="true" window-seconds="300"/>
</h235-config>
```

**TLS/IPsec**:
```xml
<transport-security>
  <tls enabled="true" version="1.2,1.3"/>
  <cipher-suites>
    TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384,
    TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256
  </cipher-suites>
  <mutual-auth enabled="true"/>
</transport-security>
```

**PKI Configuration**:
```xml
<pki-config>
  <certificate path="/etc/certs/gatekeeper.pem"/>
  <private-key path="/etc/certs/gatekeeper-key.pem" encrypted="true"/>
  <ca-bundle path="/etc/certs/ca-bundle.pem"/>
  <crl-check enabled="true" fail-closed="true"/>
  <ocsp-check enabled="true" url="http://ocsp.example.com"/>
</pki-config>
```

### 2.2 Routing Configuration

**Alias Mappings**:
```xml
<alias-mappings>
  <alias h323-id="ep-conference-room-101" ip="10.1.50.25"/>
  <alias h323-id="ep-executive-office-201" ip="10.1.50.30"/>
  <alias e164="+14085551001" h323-id="ep-conference-room-101"/>
  <alias e164="+14085551002" h323-id="ep-executive-office-201"/>
</alias-mappings>
```

**E.164 Routing**:
```xml
<e164-routing>
  <route prefix="+1408" action="local"/>
  <route prefix="+1650" action="forward" destination="gk-branch.example.com"/>
  <route prefix="+1800" action="gateway" destination="gw-pstn-01"/>
  <route prefix="+1900" action="deny" reason="premium-rate-blocked"/>
</e164-routing>
```

**LRQ/LCF Rules**:
```xml
<inter-zone-routing>
  <zone name="branch-office" gk-address="gk-branch.example.com" tls="true"/>
  <lrq-forwarding enabled="true" timeout-seconds="5"/>
</inter-zone-routing>
```

### 2.3 Admission Control

```xml
<admission-control>
  <bandwidth>
    <per-call max-kbps="2048"/>
    <per-endpoint max-kbps="10240" max-calls="5"/>
    <per-gateway max-kbps="51200" max-calls="100"/>
    <total max-kbps="102400"/>
  </bandwidth>
  <call-model>gatekeeper-routed</call-model>
  <arq-timeout-seconds>30</arq-timeout-seconds>
</admission-control>
```

### 2.4 Logging Configuration

```xml
<logging>
  <log-level>INFO</log-level>
  <log-categories>
    <category name="RAS" enabled="true"/>
    <category name="H.225" enabled="true"/>
    <category name="H.235" enabled="true"/>
    <category name="SECURITY" enabled="true"/>
  </log-categories>
  <syslog>
    <server address="siem.example.com" port="6514" protocol="tls"/>
    <format>json</format>
  </syslog>
</logging>
```

---

## 3. Gateway Baseline Configuration

### 3.1 Security Configuration

**H.235 Profiles**:
```xml
<h235-config>
  <profile name="H.235.2" enabled="true" mandatory="true"/>
  <profile name="H.235.3" enabled="true" mandatory="true"/>
  <profile name="H.235.4" enabled="true" mandatory="true"/>
  <profile name="H.235.6" enabled="true" mandatory="true"/>
  <srtp-fallback-to-rtp enabled="false"/>
</h235-config>
```

**SRTP Configuration**:
```xml
<srtp-config>
  <crypto-suite>AES_CM_128_HMAC_SHA1_80</crypto-suite>
  <crypto-suite>AES_CM_256_HMAC_SHA1_80</crypto-suite>
  <key-exchange>h245</key-exchange>
  <mandatory>true</mandatory>
</srtp-config>
```

**PKI Configuration**:
```xml
<pki-config>
  <certificate path="/etc/certs/gateway.pem"/>
  <private-key path="/etc/certs/gateway-key.pem" encrypted="true"/>
  <ca-bundle path="/etc/certs/ca-bundle.pem"/>
  <crl-check enabled="true"/>
  <ocsp-check enabled="true"/>
  <mutual-tls-with-gk enabled="true"/>
</pki-config>
```

### 3.2 Trunk Configuration

**PSTN Trunk (PRI)**:
```xml
<trunk name="PRI-1" type="isdn-pri">
  <interface>T1-0/0/0</interface>
  <channels>23</channels>
  <signaling>isdn-pri</signaling>
  <switch-type>national</switch-type>
  <framing>esf</framing>
  <line-coding>b8zs</line-coding>
</trunk>
```

**SIP Trunk**:
```xml
<trunk name="SIP-CARRIER" type="sip">
  <destination>sip.carrier.com:5061</destination>
  <transport>tls</transport>
  <authentication method="digest">
    <username>gateway01</username>
    <password encrypted="true">...</password>
  </authentication>
  <srtp mandatory="true"/>
</trunk>
```

**H.320 Trunk (ISDN)**:
```xml
<trunk name="H320-ISDN" type="h320">
  <interface>E1-0/1/0</interface>
  <channels>30</channels>
  <bonding>384kbps</bonding>
  <h221-multiplex enabled="true"/>
</trunk>
```

### 3.3 Codec Mapping

```xml
<codec-mapping>
  <audio>
    <codec name="G.711u" priority="1" ptime="20"/>
    <codec name="G.711a" priority="2" ptime="20"/>
    <codec name="G.729" priority="3" ptime="20"/>
  </audio>
  <video>
    <codec name="H.264" priority="1" profile="baseline" level="3.1"/>
    <codec name="H.263" priority="2"/>
  </video>
</codec-mapping>
```

### 3.4 Gatekeeper Registration

```xml
<gatekeeper-registration>
  <gk-address>gk-primary.example.com</gk-address>
  <gk-backup>gk-secondary.example.com</gk-backup>
  <register-interval-seconds>3600</register-interval-seconds>
  <h235-auth enabled="true"/>
</gatekeeper-registration>
```

### 3.5 CDR Configuration

```xml
<cdr-config>
  <enabled>true</enabled>
  <export-to>
    <syslog address="siem.example.com" port="6514" protocol="tls"/>
  </export-to>
  <format>json</format>
  <fields>
    call_id, start_time, end_time, duration, source, destination,
    codec, gateway_id, trunk_id, cause_code
  </fields>
</cdr-config>
```

### 3.6 Logging Configuration

```xml
<logging>
  <log-level>INFO</log-level>
  <log-categories>
    <category name="H.225" enabled="true"/>
    <category name="H.245" enabled="true"/>
    <category name="SRTP" enabled="true"/>
    <category name="TRUNK" enabled="true"/>
    <category name="SECURITY" enabled="true"/>
  </log-categories>
  <syslog>
    <server address="siem.example.com" port="6514" protocol="tls"/>
    <format>json</format>
  </syslog>
</logging>
```

---

## 4. Endpoint Baseline Configuration

### 4.1 Security Configuration

**PKI Configuration**:
```xml
<pki-config>
  <certificate path="/config/certs/endpoint.pem"/>
  <ca-bundle path="/config/certs/ca-bundle.pem"/>
  <crl-check enabled="true"/>
  <ocsp-check enabled="true"/>
</pki-config>
```

**H.235 Configuration**:
```xml
<h235-config>
  <h235-2 enabled="true"/>
  <h235-3 enabled="true"/>
  <h235-4 enabled="true"/>
  <srtp enabled="true" mandatory="true"/>
</h235-config>
```

### 4.2 Gatekeeper Configuration

```xml
<gatekeeper>
  <address>gk-primary.example.com</address>
  <backup>gk-secondary.example.com</backup>
  <auto-register enabled="true"/>
  <register-interval-seconds>3600</register-interval-seconds>
</gatekeeper>
```

### 4.3 Codec Configuration

```xml
<codecs>
  <audio>
    <codec name="G.711u" enabled="true"/>
    <codec name="G.722" enabled="true"/>
    <codec name="G.729" enabled="false"/>
  </audio>
  <video>
    <codec name="H.264" enabled="true"/>
    <max-bitrate-kbps>2048</max-bitrate-kbps>
    <resolution>1080p</resolution>
  </video>
</codecs>
```

### 4.4 Local Security Configuration

```xml
<local-security>
  <admin-ui locked="true">
    <password min-length="12" complexity="high"/>
  </admin-ui>
  <auto-answer enabled="false"/>
  <external-control enabled="false"/>
  <web-ui https-only="true" tls-version="1.2"/>
</local-security>
```

### 4.5 Network Configuration

```xml
<network>
  <vlan id="50" priority="6"/>
  <qos dscp="ef" /> <!-- Voice -->
  <qos-video dscp="af41" /> <!-- Video -->
  <ntp server="ntp.example.com" />
</network>
```

---

## 5. Baseline Validation

### 5.1 Gatekeeper Validation

**Security Checks**:
```bash
# Validate H.235 enabled
gk-cli show h235-status
# Expected: H.235.2/3/4 enabled, mandatory

# Validate TLS enabled
gk-cli show tls-config
# Expected: TLS 1.2+, mutual auth enabled

# Validate certificate
openssl x509 -in /etc/certs/gatekeeper.pem -noout -text
# Expected: Valid, not expired, correct SAN
```

**Functional Checks**:
```bash
# Check registrations
gk-cli show registrations
# Expected: All endpoints registered with valid H.235 tokens

# Check routing
gk-cli show routes
# Expected: All routes defined per baseline
```

### 5.2 Gateway Validation

**Security Checks**:
```bash
# Validate SRTP mandatory
gw-cli show srtp-config
# Expected: SRTP mandatory, no RTP fallback

# Validate trunk status
gw-cli show trunk-status
# Expected: All trunks up

# Validate certificate
openssl x509 -in /etc/certs/gateway.pem -noout -text
# Expected: Valid, not expired
```

**Functional Checks**:
```bash
# Test call to PSTN
gw-cli test-call +18005551234
# Expected: Call succeeds, SRTP active

# Validate CDR export
gw-cli show cdr-export
# Expected: Logs flowing to SIEM
```

### 5.3 Endpoint Validation

**Security Checks**:
```bash
# Validate SRTP enabled
ep-cli show srtp-status
# Expected: SRTP enabled, mandatory

# Validate registration
ep-cli show registration
# Expected: Registered with GK, H.235 auth
```

**Functional Checks**:
```bash
# Test call to another endpoint
ep-cli test-call ep-conference-room-102
# Expected: Call succeeds, SRTP active
```

---

## 6. Baseline Deviation Management

### 6.1 Detecting Deviations

**Automated Scanning**:
```bash
# Compare current config vs. baseline
config-audit --baseline /baselines/gk-baseline.xml --current /etc/gk/config.xml
# Output: List of deviations
```

**Manual Inspection**:

- Quarterly configuration audits
- Review change logs
- Validate against hardening checklist

### 6.2 Remediating Deviations

**Unauthorized Changes**:

1. Investigate change (who, when, why)
1. Assess security impact
1. Revert to baseline (if unauthorized)
1. Update baseline (if authorized change)

**Configuration Drift**:

1. Detect drift via automated scan
1. Remediate via configuration management tool
1. Validate compliance post-remediation

---

## 7. Baseline Maintenance

### 7.1 Baseline Updates

**Triggers for Baseline Updates**:

- Security advisory (vendor or enterprise)
- New feature deployment
- Regulatory requirement change
- Incident response recommendation

**Update Process**:

1. Propose baseline change
1. Review by architecture board
1. Test in lab environment
1. Update baseline documentation
1. Roll out to production (change control)

### 7.2 Baseline Versioning

**Version Numbering**:

- Major.Minor.Patch (e.g., 1.2.3)
- Major: Significant security or architecture change
- Minor: Feature addition or enhancement
- Patch: Bug fix or minor adjustment

**Version Control**:

- Store baselines in Git
- Tag each version
- Maintain change log

---

## 8. Completion Criteria

Baseline configurations are considered compliant when:

- All components configured per baseline
- All security controls validated
- All functional tests pass
- Configuration drift < 5%
- All deviations documented and approved
- Baseline version controlled
- Validation automated where possible
