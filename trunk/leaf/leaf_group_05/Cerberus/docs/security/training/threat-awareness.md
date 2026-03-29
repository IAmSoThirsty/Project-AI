<!-- # ============================================================================ # -->
<!-- # STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59 # -->
<!-- # COMPLIANCE: Sovereign Substrate / threat-awareness.md # -->
<!-- # ============================================================================ # -->
<div align="right">
  <img src="https://img.shields.io/badge/DATE-2026-03-18-blueviolet?style=for-the-badge" alt="Date" />
  <img src="https://img.shields.io/badge/PRODUCTIVITY-ACTIVE-success?style=for-the-badge" alt="Productivity" />
</div>
<!-- # ============================================================================ #


<!-- # COMPLIANCE: Sovereign Substrate / threat-awareness.md # -->
<!-- # ============================================================================ #

<!-- # Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master -->
# Threat Awareness Training

## Table of Contents
1. [Learning Objectives](#learning-objectives)
2. [Threat Landscape](#threat-landscape)
3. [Attack Scenarios](#attack-scenarios)
4. [Social Engineering & Phishing](#social-engineering--phishing)
5. [Insider Threats](#insider-threats)
6. [Cerberus Guardian Detection](#cerberus-guardian-detection)
7. [Real-World Case Studies](#real-world-case-studies)
8. [Assessment Activities](#assessment-activities)

---

## Learning Objectives

By completing this threat awareness training, participants will be able to:

- **Recognize common threat types** and attack vectors
- **Identify social engineering and phishing attempts**
- **Understand insider threat indicators**
- **Apply Cerberus Guardians** for threat detection
- **Respond appropriately** to suspected threats
- **Report security incidents** correctly
- **Protect personal and organizational data** from threats
- **Understand the business impact** of security breaches

---

## Threat Landscape

### 1.1 Threat Classification

Security threats can be classified by:

**By Threat Actor**

1. **External Threats**
   - Cybercriminals: Motivated by financial gain
   - Nation-state actors: State-sponsored espionage
   - Hacktivists: Politically motivated attackers
   - Script kiddies: Unskilled attackers using tools
   - Competitors: Industrial espionage

2. **Internal Threats**
   - Malicious insiders: Employees stealing data
   - Negligent employees: Unintentional mistakes
   - Compromised accounts: Legitimate accounts used by attackers
   - Third-party vendors: Contractors with access

**By Threat Type**

1. **Malware**
   - Viruses: Self-replicating code attached to files
   - Worms: Self-propagating across networks
   - Trojans: Disguised malicious programs
   - Ransomware: Encrypts data for extortion
   - Spyware: Monitors user activity
   - Adware: Displays unwanted advertisements
   - Rootkits: Gains root/admin access

2. **Web-Based Attacks**
   - SQL Injection: Manipulates database queries
   - Cross-Site Scripting (XSS): Injects malicious scripts
   - Cross-Site Request Forgery (CSRF): Forges unauthorized requests
   - Man-in-the-Middle (MITM): Intercepts communications
   - Denial of Service (DoS): Overwhelms systems with traffic

3. **Credential-Based Attacks**
   - Brute force: Tries all password combinations
   - Dictionary attacks: Uses common passwords
   - Credential stuffing: Uses leaked credentials
   - Phishing: Social engineering for credentials
   - Keylogging: Records keystrokes

4. **Physical Threats**
   - Unauthorized access: Entering restricted areas
   - Hardware theft: Stealing computers/devices
   - Dumpster diving: Retrieving discarded information
   - Shoulder surfing: Observing screens/inputs
   - Badge cloning: Copying access badges

### 1.2 Threat Actors & Motivations

```python
from cerberus.security import ThreatProfiler, ThreatIntelligence
from cerberus.guardians import ThreatGuardian

class ThreatActorAnalysis:
    def __init__(self):
        self.threat_profiler = ThreatProfiler()
        self.threat_intelligence = ThreatIntelligence()
        self.threat_guardian = ThreatGuardian()
    
    def analyze_threat_actor_profile(self, actor_type, motivations):
        """
        Analyze threat actor profile and characteristics.
        """
        profiles = {
            'cybercriminal': {
                'motivations': ['financial_gain', 'data_theft', 'extortion'],
                'sophistication': 'variable',
                'target_selection': 'opportunistic_or_targeted',
                'tools': ['custom_malware', 'off_the_shelf_tools'],
                'attack_patterns': ['ransomware', 'data_exfiltration', 'credential_theft']
            },
            'nation_state': {
                'motivations': ['espionage', 'sabotage', 'political_influence'],
                'sophistication': 'very_high',
                'target_selection': 'strategic',
                'tools': ['advanced_persistent_threat', 'zero_days', 'custom_malware'],
                'attack_patterns': ['data_theft', 'system_compromise', 'long_dwell_time']
            },
            'hacktivist': {
                'motivations': ['political_cause', 'activism', 'publicity'],
                'sophistication': 'variable',
                'target_selection': 'ideological',
                'tools': ['public_tools', 'crowd_sourced'],
                'attack_patterns': ['ddos', 'defacement', 'data_disclosure']
            },
            'insider': {
                'motivations': ['financial_gain', 'revenge', 'ideology'],
                'sophistication': 'high_due_to_access',
                'target_selection': 'internal_systems',
                'tools': ['legitimate_access', 'admin_tools'],
                'attack_patterns': ['data_theft', 'sabotage', 'privilege_escalation']
            }
        }
        
        profile = profiles.get(actor_type, {})
        
        # Log threat actor analysis
        self.threat_guardian.log_threat_actor_analysis(actor_type, profile)
        
        return profile
    
    def assess_attack_sophistication(self, attack_characteristics):
        """
        Assess sophistication level of attack.
        """
        indicators = {
            'very_high': [
                'zero_day_exploits',
                'custom_malware',
                'advanced_evasion',
                'multi_stage_attack',
                'supply_chain_compromise'
            ],
            'high': [
                'unpatched_vulnerability_exploitation',
                'advanced_social_engineering',
                'lateral_movement',
                'credential_harvesting',
                'data_exfiltration_tools'
            ],
            'medium': [
                'known_vulnerability_exploitation',
                'phishing_campaigns',
                'password_attacks',
                'public_malware_variants'
            ],
            'low': [
                'script_kiddie_tools',
                'automated_scanning',
                'basic_phishing',
                'weak_password_guessing'
            ]
        }
        
        # Determine sophistication level
        for level, indicators_list in indicators.items():
            if any(char in attack_characteristics for char in indicators_list):
                self.threat_guardian.log_sophistication_assessment(
                    level,
                    attack_characteristics
                )
                return level
        
        return 'unknown'
```

### 1.3 Attack Surfaces

Understanding attack surfaces helps identify where to focus security efforts.

**Common Attack Surfaces:**

1. **Network Layer**
   - Exposed services (SSH, RDP, databases)
   - Unencrypted communications
   - DNS hijacking
   - BGP hijacking

2. **Application Layer**
   - Input validation flaws
   - Authentication bypasses
   - Authorization flaws
   - Business logic vulnerabilities

3. **Data Layer**
   - Unencrypted sensitive data
   - Weak database access controls
   - Data in transit vulnerabilities
   - Backup data exposure

4. **Infrastructure Layer**
   - Misconfigured cloud resources
   - Unpatched systems
   - Default credentials
   - Weak container security

5. **Social Layer**
   - Employee vulnerabilities
   - Contractor access risks
   - Physical security gaps
   - Supply chain weaknesses

---

## Attack Scenarios

### 2.1 Scenario 1: Advanced Persistent Threat (APT)

**Scenario Description:**

A financial services company discovers unauthorized access to their trading systems. Investigation reveals:

- Initial compromise via spear-phishing targeting executives
- Attacker obtained VPN credentials
- Lateral movement through network for 6 months undetected
- Access to trading algorithms and non-public information
- Evidence of data exfiltration to foreign servers

**Timeline:**

```
Day 0: Executive receives convincing phishing email with malicious attachment
Day 2: Employee opens attachment, malware installed
Day 3: Attacker establishes reverse shell connection
Day 5: Attacker escalates privileges to domain admin
Day 7: Attacker begins lateral movement across network
Day 10: Attacker gains access to trading system database
Day 15: Attacker exfiltrates trading algorithms and market data
Day 180: Unauthorized trading activity detected during audit
Day 182: Intrusion discovery and response activation
```

**Cerberus Detection:**

```python
from cerberus.guardians import APTGuardian, AnomalyDetectionGuardian
from cerberus.security import BehavioralAnalysis

class APTDetection:
    def __init__(self):
        self.apt_guardian = APTGuardian()
        self.anomaly_guardian = AnomalyDetectionGuardian()
        self.behavioral_analysis = BehavioralAnalysis()
    
    def detect_apt_indicators(self, network_events):
        """
        Detect indicators of advanced persistent threat.
        """
        apt_indicators = {
            'suspicious_email_attachment': False,
            'unusual_login_pattern': False,
            'privilege_escalation_attempt': False,
            'lateral_movement_detected': False,
            'data_exfiltration_pattern': False,
            'command_control_communication': False
        }
        
        # Analyze network events
        for event in network_events:
            if self.apt_guardian.is_suspicious_attachment(event):
                apt_indicators['suspicious_email_attachment'] = True
            
            if self.apt_guardian.is_unusual_login(event):
                apt_indicators['unusual_login_pattern'] = True
            
            if self.apt_guardian.is_privilege_escalation(event):
                apt_indicators['privilege_escalation_attempt'] = True
            
            if self.apt_guardian.is_lateral_movement(event):
                apt_indicators['lateral_movement_detected'] = True
            
            if self.apt_guardian.is_data_exfiltration(event):
                apt_indicators['data_exfiltration_pattern'] = True
            
            if self.apt_guardian.is_c2_communication(event):
                apt_indicators['command_control_communication'] = True
        
        # Calculate threat score
        threat_score = sum(1 for v in apt_indicators.values() if v) / len(apt_indicators)
        
        if threat_score >= 0.5:
            self.apt_guardian.raise_apt_alert(apt_indicators, threat_score)
            return 'HIGH_APT_RISK'
        elif threat_score >= 0.3:
            self.apt_guardian.investigate_potential_apt(apt_indicators, threat_score)
            return 'POTENTIAL_APT_RISK'
        else:
            return 'LOW_APT_RISK'
    
    def respond_to_apt(self, incident_indicators):
        """
        Respond to detected APT activity.
        """
        # Step 1: Isolate affected systems
        self.apt_guardian.isolate_compromised_systems()
        
        # Step 2: Preserve evidence
        self.apt_guardian.preserve_forensic_evidence()
        
        # Step 3: Conduct forensic analysis
        forensic_report = self.apt_guardian.conduct_forensic_analysis()
        
        # Step 4: Identify compromised accounts
        compromised_accounts = self.apt_guardian.identify_compromised_accounts()
        
        # Step 5: Reset credentials
        for account in compromised_accounts:
            self.apt_guardian.force_password_reset(account)
            self.apt_guardian.revoke_all_sessions(account)
        
        # Step 6: Patch vulnerabilities
        vulnerabilities = self.apt_guardian.identify_exploitation_vulnerabilities()
        for vuln in vulnerabilities:
            self.apt_guardian.prioritize_patch(vuln)
        
        return forensic_report
```

### 2.2 Scenario 2: Ransomware Attack

**Scenario Description:**

A manufacturing company's systems are encrypted with ransomware. Investigation reveals:

- File-sharing service compromise led to credential theft
- Attacker accessed network via VPN
- Ransomware deployed across file servers
- Production systems unable to access critical files
- Attacker demands $5M for decryption key

**Impact Assessment:**

- Production halted
- Inventory systems unavailable
- Customer orders cannot be processed
- Revenue loss: ~$500,000/day
- Reputation damage
- Potential regulatory fines

**Cerberus Ransomware Response:**

```python
from cerberus.guardians import RansomwareGuardian, BackupGuardian
from cerberus.security import RecoveryManager

class RansomwareIncidentResponse:
    def __init__(self):
        self.ransomware_guardian = RansomwareGuardian()
        self.backup_guardian = BackupGuardian()
        self.recovery_manager = RecoveryManager()
    
    def detect_ransomware_activity(self, file_system_events):
        """
        Detect ransomware indicators in file system activity.
        """
        ransomware_indicators = {
            'rapid_file_encryption': False,
            'unusual_file_extensions': False,
            'ransom_note_creation': False,
            'backup_file_deletion': False,
            'file_metadata_changes': False
        }
        
        # Analyze file operations
        for event in file_system_events:
            if self.ransomware_guardian.is_rapid_encryption(event):
                ransomware_indicators['rapid_file_encryption'] = True
            
            if self.ransomware_guardian.has_unusual_extension(event):
                ransomware_indicators['unusual_file_extensions'] = True
            
            if self.ransomware_guardian.is_ransom_note(event):
                ransomware_indicators['ransom_note_creation'] = True
            
            if self.ransomware_guardian.is_backup_deletion(event):
                ransomware_indicators['backup_file_deletion'] = True
        
        # Alert if multiple indicators present
        if sum(ransomware_indicators.values()) >= 2:
            self.ransomware_guardian.raise_ransomware_alert(ransomware_indicators)
            return True
        
        return False
    
    def respond_to_ransomware(self, encryption_start_time):
        """
        Respond to ransomware incident.
        """
        response_plan = {
            'immediate': [],
            'short_term': [],
            'long_term': []
        }
        
        # Immediate actions (0-1 hour)
        response_plan['immediate'].extend([
            'Isolate all infected systems from network',
            'Disable affected user accounts',
            'Block attacker command and control domains',
            'Preserve logs and forensic evidence',
            'Notify incident response team'
        ])
        
        # Execute immediate actions
        self.ransomware_guardian.isolate_infected_systems()
        self.ransomware_guardian.disable_user_accounts()
        self.ransomware_guardian.block_c2_domains()
        
        # Short-term actions (1-24 hours)
        response_plan['short_term'].extend([
            'Assess backup integrity',
            'Identify infection entry point',
            'Determine affected systems scope',
            'Calculate recovery time and data loss',
            'Notify management and legal'
        ])
        
        # Check backup integrity
        backup_status = self.backup_guardian.verify_backup_integrity()
        
        if backup_status['is_intact']:
            response_plan['short_term'].append('Initiate recovery from clean backups')
            recovery_time = self.recovery_manager.estimate_recovery_time(
                backup_status['last_clean_backup']
            )
        else:
            response_plan['short_term'].append(
                'WARNING: Backups corrupted - contact forensics team'
            )
            recovery_time = 'UNKNOWN'
        
        # Long-term actions (1+ weeks)
        response_plan['long_term'].extend([
            'Conduct root cause analysis',
            'Identify network vulnerabilities exploited',
            'Implement preventive controls',
            'Update incident response procedures',
            'Conduct security awareness training'
        ])
        
        return response_plan
    
    def decide_ransom_payment(self, ransom_amount, incident_data):
        """
        Guidelines for deciding on ransom payment.
        """
        decision_factors = {
            'backups_available': self.backup_guardian.has_valid_backups(),
            'recovery_time': incident_data.get('recovery_time'),
            'business_impact': incident_data.get('business_impact'),
            'law_enforcement_advice': self.ransomware_guardian.get_law_enforcement_recommendation(),
            'ransom_tracking': self.ransomware_guardian.can_track_ransom()
        }
        
        recommendation = "DO NOT PAY RANSOM"
        
        reasoning = [
            "Paying ransom encourages future attacks",
            "No guarantee attacker will provide decryption key",
            "Recovery from backups is faster and more reliable",
            "Ransom payments may violate regulations",
            "Law enforcement can assist with recovery"
        ]
        
        # Only exception: critical business systems, no backups, severe impact
        if (decision_factors['backups_available'] is False and 
            incident_data.get('business_impact') == 'CRITICAL' and
            recovery_time == 'EXTENDED'):
            recommendation = "CONSULT LAW ENFORCEMENT AND LEGAL"
        
        return {
            'recommendation': recommendation,
            'reasoning': reasoning,
            'decision_factors': decision_factors
        }
```

### 2.3 Scenario 3: Data Breach

**Scenario Description:**

A healthcare provider discovers that patient medical records were stolen. Investigation reveals:

- Unencrypted database backup was stored on public S3 bucket
- Backup contained 2.5 million patient records
- Records included: names, SSNs, diagnoses, medications
- Attacker published sample records online
- Breach detected after records appeared on dark web

**Regulatory Impact:**

- HIPAA violation: Up to $1.5M per violation
- State notification laws triggered: Notify all patients
- Credit monitoring costs: $10+ per patient
- Lawsuits and settlements: Millions
- Reputational damage: Loss of patient trust

**Cerberus Data Protection:**

```python
from cerberus.guardians import DataClassificationGuardian, EncryptionGuardian
from cerberus.security import DataInventory, SensitiveDataDetector

class DataBreachPrevention:
    def __init__(self):
        self.data_classification = DataClassificationGuardian()
        self.encryption_guardian = EncryptionGuardian()
        self.data_inventory = DataInventory()
        self.sensitive_data_detector = SensitiveDataDetector()
    
    def classify_sensitive_data(self):
        """
        Classify all data by sensitivity level.
        """
        classification_levels = {
            'public': {
                'description': 'Can be publicly disclosed',
                'encryption_required': False,
                'access_control': 'low',
                'examples': ['marketing materials', 'public announcements']
            },
            'internal': {
                'description': 'For internal use only',
                'encryption_required': True,
                'access_control': 'medium',
                'examples': ['internal policies', 'org charts']
            },
            'confidential': {
                'description': 'Business sensitive data',
                'encryption_required': True,
                'access_control': 'high',
                'examples': ['financial data', 'contracts']
            },
            'restricted': {
                'description': 'Regulated sensitive data',
                'encryption_required': True,
                'access_control': 'very_high',
                'examples': ['medical records', 'payment card data', 'PII']
            }
        }
        
        # Scan all data stores
        data_inventory = self.data_inventory.get_all_data_locations()
        
        for data_location in data_inventory:
            # Detect sensitive data automatically
            detected_data = self.sensitive_data_detector.scan(data_location)
            
            for data_item in detected_data:
                # Classify sensitivity
                classification = self.data_classification.classify(data_item)
                
                # Apply protection requirements
                protection_config = classification_levels[classification]
                
                # Ensure encryption
                if protection_config['encryption_required']:
                    self.encryption_guardian.ensure_encryption(
                        data_item,
                        encryption_algorithm='AES-256'
                    )
                
                # Restrict access
                self.data_classification.apply_access_restrictions(
                    data_item,
                    access_level=protection_config['access_control']
                )
                
                self.data_classification.log_classification(
                    data_item,
                    classification
                )
    
    def prevent_data_exposure(self):
        """
        Prevent common data exposure scenarios.
        """
        prevention_measures = [
            {
                'threat': 'Unencrypted data in transit',
                'prevention': 'Enforce TLS 1.2+ for all communications'
            },
            {
                'threat': 'Unencrypted data at rest',
                'prevention': 'Encrypt all sensitive data with AES-256'
            },
            {
                'threat': 'Exposed backups',
                'prevention': 'Store backups in encrypted, access-restricted locations'
            },
            {
                'threat': 'Excessive access permissions',
                'prevention': 'Apply principle of least privilege'
            },
            {
                'threat': 'Unencrypted database fields',
                'prevention': 'Encrypt PII fields: SSN, credit card, medical data'
            },
            {
                'threat': 'Public S3 buckets',
                'prevention': 'Scan regularly for misconfigured cloud storage'
            },
            {
                'threat': 'Data in logs',
                'prevention': 'Redact sensitive data from all logs'
            }
        ]
        
        for measure in prevention_measures:
            self.data_classification.implement_prevention(measure)
```

---

## Social Engineering & Phishing

### 3.1 Social Engineering Tactics

Social engineering exploits human psychology rather than technical vulnerabilities.

**Common Tactics:**

1. **Pretexting**
   - Creating false scenarios to build trust
   - "I'm calling from IT with an urgent system issue"
   - "I'm a new contractor needing system access"

2. **Baiting**
   - Offering something desirable to trigger response
   - USB drives with malware left in parking lot
   - Free Wi-Fi networks in public places

3. **Tailgating/Piggybacking**
   - Following authorized person through secure door
   - "I'm with the IT repair team"
   - Following employees into secure areas

4. **Reverse Social Engineering**
   - Creating problem, then offering solution
   - "Your system has a critical vulnerability - let me access it"
   - Sabotaging system, then offering fix

5. **Quid Pro Quo**
   - Trading favors for information
   - "Help me access the system and I'll give you concert tickets"
   - Offering services in exchange for access

### 3.2 Phishing Attacks

Phishing is a mass social engineering attack using email or messages.

**Types of Phishing:**

**Email Phishing**

```python
from cerberus.guardians import PhishingGuardian, EmailSecurityGuardian
from cerberus.security import URLAnalyzer, AttachmentScanner

class PhishingDetection:
    def __init__(self):
        self.phishing_guardian = PhishingGuardian()
        self.email_security = EmailSecurityGuardian()
        self.url_analyzer = URLAnalyzer()
        self.attachment_scanner = AttachmentScanner()
    
    def analyze_email_for_phishing(self, email_message):
        """
        Analyze email for phishing indicators.
        """
        phishing_indicators = {
            'sender_spoofing': False,
            'suspicious_links': [],
            'malicious_attachments': [],
            'urgency_language': False,
            'requests_sensitive_info': False,
            'grammar_spelling_errors': False,
            'mismatched_domains': False
        }
        
        # Check sender reputation
        if not self.phishing_guardian.is_trusted_sender(email_message['from']):
            phishing_indicators['sender_spoofing'] = True
        
        # Analyze links
        for link in self.email_security.extract_links(email_message):
            if self.url_analyzer.is_phishing_url(link):
                phishing_indicators['suspicious_links'].append(link)
        
        # Scan attachments
        for attachment in email_message.get('attachments', []):
            if self.attachment_scanner.is_malicious(attachment):
                phishing_indicators['malicious_attachments'].append(
                    attachment['name']
                )
        
        # Detect urgency language
        urgent_phrases = [
            'immediate action required',
            'verify account',
            'confirm identity',
            'unusual activity',
            'click here now',
            'limited time'
        ]
        
        email_body = email_message['body'].lower()
        
        for phrase in urgent_phrases:
            if phrase in email_body:
                phishing_indicators['urgency_language'] = True
                break
        
        # Detect requests for sensitive information
        sensitive_requests = [
            'password',
            'credit card',
            'ssn',
            'account number',
            'verification code'
        ]
        
        for request in sensitive_requests:
            if request in email_body:
                phishing_indicators['requests_sensitive_info'] = True
                break
        
        # Check for grammar/spelling errors
        if self.phishing_guardian.has_grammar_errors(email_body):
            phishing_indicators['grammar_spelling_errors'] = True
        
        # Check domain mismatches
        if self.phishing_guardian.has_domain_mismatch(
            email_message['from'],
            phishing_indicators['suspicious_links']
        ):
            phishing_indicators['mismatched_domains'] = True
        
        # Calculate phishing score
        phishing_score = self.calculate_phishing_score(phishing_indicators)
        
        if phishing_score >= 0.8:
            self.phishing_guardian.quarantine_email(email_message)
            self.phishing_guardian.alert_user('PHISHING DETECTED')
            return 'PHISHING'
        elif phishing_score >= 0.5:
            self.phishing_guardian.flag_suspicious_email(email_message)
            return 'SUSPICIOUS'
        else:
            return 'LEGITIMATE'
    
    def calculate_phishing_score(self, indicators):
        """
        Calculate overall phishing score (0-1).
        """
        weights = {
            'sender_spoofing': 0.3,
            'suspicious_links': 0.25,
            'malicious_attachments': 0.25,
            'urgency_language': 0.1,
            'requests_sensitive_info': 0.15,
            'grammar_spelling_errors': 0.05,
            'mismatched_domains': 0.2
        }
        
        score = 0.0
        
        if indicators['sender_spoofing']:
            score += weights['sender_spoofing']
        
        if indicators['suspicious_links']:
            score += min(0.25, len(indicators['suspicious_links']) * 0.1)
        
        if indicators['malicious_attachments']:
            score += weights['malicious_attachments']
        
        if indicators['urgency_language']:
            score += weights['urgency_language']
        
        if indicators['requests_sensitive_info']:
            score += weights['requests_sensitive_info']
        
        if indicators['grammar_spelling_errors']:
            score += weights['grammar_spelling_errors']
        
        if indicators['mismatched_domains']:
            score += weights['mismatched_domains']
        
        return min(1.0, score)
```

**Spear Phishing**

Targeted phishing at specific individuals:

```python
class SpearPhishingDetection:
    def __init__(self):
        self.phishing_guardian = PhishingGuardian()
        self.threat_intelligence = ThreatIntelligence()
    
    def detect_spear_phishing(self, email_message, recipient_profile):
        """
        Detect spear phishing targeted at specific individual.
        """
        indicators = {
            'personal_details': False,
            'role_specific_content': False,
            'organization_references': False,
            'recent_event_references': False
        }
        
        # Check if email references personal details
        personal_terms = recipient_profile.get('personal_interests', [])
        email_body = email_message['body'].lower()
        
        for term in personal_terms:
            if term in email_body:
                indicators['personal_details'] = True
        
        # Check for role-specific content
        role = recipient_profile.get('job_role')
        if role and role.lower() in email_body:
            indicators['role_specific_content'] = True
        
        # Check for organization references
        org_name = recipient_profile.get('organization')
        if org_name and org_name.lower() in email_body:
            indicators['organization_references'] = True
        
        # Check if email references recent events
        recent_events = self.threat_intelligence.get_recent_organization_events(
            recipient_profile['organization']
        )
        
        for event in recent_events:
            if event['description'].lower() in email_body:
                indicators['recent_event_references'] = True
        
        # Spear phishing likely if multiple indicators present
        if sum(indicators.values()) >= 2:
            self.phishing_guardian.raise_spear_phishing_alert(
                email_message,
                recipient_profile,
                indicators
            )
            return True
        
        return False
```

**Whaling**

Phishing targeted at high-value targets (executives):

```
Example Whaling Email:

From: "Board Member" <board-member@company.com>
Subject: Urgent - Wire Transfer Authorization Needed

Mr. CEO,

I need you to authorize an urgent wire transfer for a confidential acquisition.
Due to the sensitive nature of this deal, I cannot discuss details by phone.

Please wire $2.5M to the following account and confirm receipt:

Bank: International Trust Bank
Account: 4812956374
Routing: 021923847

This is time-sensitive and must be completed today.

- "Board Member"

INDICATORS:
✓ Urgency and time pressure
✓ Confidentiality excuse (prevents verification)
✓ CEO/executive targeted (high financial authority)
✓ Specific wire transfer details
✓ Generic greeting (not personalized)
✓ Vague sender identity
```

---

## Insider Threats

### 4.1 Insider Threat Categories

**Malicious Insiders**

- Intentionally steal data or sabotage systems
- Motivation: Financial gain, revenge, ideology
- High damage potential due to legitimate access

**Negligent Insiders**

- Unintentionally expose data or compromise security
- Motivation: None (accidental)
- High frequency but often lower impact

**Compromised Insiders**

- Legitimate employees whose accounts were compromised
- Attacker uses credentials to access systems
- May appear as insider threat while being external attack

### 4.2 Insider Threat Indicators

```python
from cerberus.guardians import InsiderThreatGuardian, BehavioralAnalyticsGuardian
from cerberus.security import EmployeeProfiler, AccessPatternAnalyzer

class InsiderThreatDetection:
    def __init__(self):
        self.insider_guardian = InsiderThreatGuardian()
        self.behavioral_analytics = BehavioralAnalyticsGuardian()
        self.employee_profiler = EmployeeProfiler()
        self.access_analyzer = AccessPatternAnalyzer()
    
    def analyze_insider_threat_indicators(self, employee_id):
        """
        Analyze behavioral and access indicators for insider threat.
        """
        risk_indicators = {
            'behavioral': [],
            'access_pattern': [],
            'data_access': [],
            'system_activity': []
        }
        
        # Get employee profile and access patterns
        employee = self.employee_profiler.get_profile(employee_id)
        access_history = self.access_analyzer.get_access_history(employee_id)
        
        # BEHAVIORAL INDICATORS
        behavioral_red_flags = [
            'recently_disciplined',
            'pending_termination',
            'demotion_or_transfer',
            'personal_financial_stress',
            'social_isolation',
            'excessive_working_hours',
            'excessive_after_hours_access',
            'frequent_access_denial_incidents'
        ]
        
        for flag in behavioral_red_flags:
            if self.insider_guardian.has_behavioral_flag(employee_id, flag):
                risk_indicators['behavioral'].append(flag)
        
        # ACCESS PATTERN INDICATORS
        # Compare to baseline behavior
        normal_patterns = self.access_analyzer.get_normal_access_patterns(
            employee_id
        )
        current_patterns = self.access_analyzer.get_current_access_patterns(
            employee_id
        )
        
        anomalies = self.access_analyzer.detect_anomalies(
            normal_patterns,
            current_patterns
        )
        
        for anomaly in anomalies:
            risk_indicators['access_pattern'].append(anomaly)
        
        # DATA ACCESS INDICATORS
        # Unusual access to sensitive data
        sensitive_data_access = self.insider_guardian.analyze_sensitive_data_access(
            employee_id
        )
        
        if sensitive_data_access.get('unusual_access'):
            risk_indicators['data_access'].extend([
                'accessing_unrelated_data',
                'accessing_restricted_data',
                'accessing_large_data_volumes',
                'accessing_data_before_leaving'
            ])
        
        # SYSTEM ACTIVITY INDICATORS
        system_activities = self.insider_guardian.analyze_system_activities(
            employee_id
        )
        
        suspicious_activities = [
            'attempted_privilege_escalation',
            'disabling_security_tools',
            'accessing_password_manager',
            'copying_sensitive_files',
            'emailing_sensitive_data',
            'uploading_to_personal_cloud',
            'printing_sensitive_documents'
        ]
        
        for activity in suspicious_activities:
            if system_activities.get(activity):
                risk_indicators['system_activity'].append(activity)
        
        # Calculate insider threat risk score
        risk_score = self.calculate_insider_threat_score(risk_indicators)
        
        if risk_score >= 0.8:
            self.insider_guardian.escalate_to_management(
                employee_id,
                risk_indicators,
                risk_score
            )
            return 'HIGH_RISK'
        elif risk_score >= 0.5:
            self.insider_guardian.monitor_employee(employee_id, risk_indicators)
            return 'MEDIUM_RISK'
        else:
            return 'LOW_RISK'
    
    def calculate_insider_threat_score(self, indicators):
        """
        Calculate insider threat risk score (0-1).
        """
        weights = {
            'behavioral': 0.3,
            'access_pattern': 0.25,
            'data_access': 0.3,
            'system_activity': 0.15
        }
        
        score = 0.0
        
        for category, weight in weights.items():
            if indicators[category]:
                # Score increases based on number of indicators
                category_score = min(1.0, len(indicators[category]) * 0.2)
                score += weight * category_score
        
        return min(1.0, score)
```

### 4.3 Insider Threat Prevention

**Preventive Measures:**

1. **Access Control**
   - Implement principle of least privilege
   - Regular access reviews and removal
   - Segregation of duties

2. **Monitoring**
   - User activity monitoring (UAM)
   - Data access logging
   - Behavioral analytics

3. **Technical Controls**
   - Endpoint protection
   - Data loss prevention (DLP)
   - Encrypted communications monitoring

4. **Administrative Controls**
   - Background checks
   - Employment contracts with NDA
   - Regular security training
   - Clear consequences for violations

5. **Psychological Controls**
   - Positive workplace culture
   - Employee assistance programs
   - Fair compensation and benefits
   - Recognition and career development

---

## Cerberus Guardian Detection

### 5.1 Guardian Threat Detection Workflow

```python
from cerberus.guardians import (
    ThreatDetectionGuardian,
    IncidentResponseGuardian,
    ForensicsGuardian
)

class CerberusUnifiedThreatDetection:
    def __init__(self):
        self.threat_detection = ThreatDetectionGuardian()
        self.incident_response = IncidentResponseGuardian()
        self.forensics = ForensicsGuardian()
    
    def unified_threat_detection_workflow(self, security_event):
        """
        Cerberus unified workflow for detecting and responding to threats.
        """
        # Step 1: Event Detection & Collection
        detection = self.threat_detection.detect_event(security_event)
        
        if not detection['is_threat']:
            return 'benign_event'
        
        # Step 2: Threat Analysis & Classification
        threat_analysis = self.threat_detection.analyze_threat(detection)
        threat_type = threat_analysis['threat_type']  # APT, malware, etc.
        severity = threat_analysis['severity']  # critical, high, medium, low
        
        # Step 3: Incident Creation & Tracking
        incident = self.incident_response.create_incident(
            threat_type=threat_type,
            severity=severity,
            initial_event=security_event,
            threat_analysis=threat_analysis
        )
        
        # Step 4: Containment
        self.incident_response.execute_containment(incident)
        
        # Step 5: Evidence Preservation
        self.forensics.preserve_evidence(incident)
        
        # Step 6: Investigation & Attribution
        investigation = self.forensics.conduct_investigation(incident)
        
        # Step 7: Response Execution
        response_actions = self.incident_response.determine_response_actions(
            threat_type,
            investigation
        )
        
        self.incident_response.execute_response(incident, response_actions)
        
        # Step 8: Recovery
        if severity == 'critical':
            self.incident_response.execute_recovery_plan(incident)
        
        # Step 9: Post-Incident Analysis
        lessons_learned = self.incident_response.conduct_post_incident_review(
            incident
        )
        
        return {
            'incident_id': incident['id'],
            'threat_type': threat_type,
            'severity': severity,
            'response_status': 'completed',
            'lessons_learned': lessons_learned
        }
```

---

## Real-World Case Studies

### 6.1 Case Study 1: Target Data Breach (2013)

**What Happened:**

- Attackers stole 40 million credit card numbers and personal info for 70 million customers
- Entry point: Compromised HVAC contractor credentials
- Lateral movement through network for weeks
- Access to payment card processing system

**Timeline:**

```
July 2013: Attackers gain access via HVAC contractor
           credentials - network reconnaissance begins

October: Attackers deploy malware on Point of Sale (POS) systems

       : Data exfiltration begins - 40 million cards stolen
       
       : Data published on underground forums

December 15: Target discovers unauthorized activity
December 19: Target confirms data breach
December 22: Target notifies public and law enforcement
```

**Impact:**

- 40+ million credit cards compromised
- 70 million customer records stolen
- $18.5M settlement
- CEO resignation
- Massive reputation damage

**Lessons:**

- Third-party vendor access must be strictly controlled and monitored
- Network segmentation: Payment system should be isolated
- Behavioral analytics could detect data exfiltration
- Incident response was too slow (2+ months before detection)

### 6.2 Case Study 2: Equifax Breach (2017)

**What Happened:**

- Hackers exploited known vulnerability in Apache Struts web framework
- Accessed personal data: names, SSNs, dates of birth, addresses
- 147 million people affected
- Breach undetected for ~2 months

**Timeline:**

```
March 2017: Apache Struts vulnerability discovered and patched
           - Equifax didn't patch systems

May 2017: Attacker discovers vulnerable Equifax system
         : Begins exfiltrating data

July 29: Equifax discovers suspicious activity
        : Realizes massive data breach occurred
        
September 7: Breach announced publicly
             : Backlash and investigations begin
```

**Impact:**

- 147 million people affected
- $700M settlement
- Criminal investigations launched
- Class action lawsuits
- Massive erosion of trust in credit reporting

**Lessons:**

- Patch management is critical - don't delay applying security patches
- Data minimization: Collect/store only necessary data
- Breach notification should be prompt and transparent
- Large data repositories are high-value targets
- Encryption could have reduced damage

### 6.3 Case Study 3: SolarWinds Supply Chain Attack (2020)

**What Happened:**

- Attackers compromised SolarWinds build system
- Infected software updates delivered to 18,000+ customers
- Advanced persistent threat targeting U.S. government, intelligence agencies, Fortune 500
- Dwell time: 8+ months before detection

**Attack Chain:**

```
October 2019: Attackers compromise SolarWinds build infrastructure

             : Inject malicious code into Orion software

March 2020: Malicious updates distributed to 18,000+ customers
           : Malware installed on customer networks

             : Command and control (C2) communication established
             
             : Lateral movement and privilege escalation begins

December 8, 2020: FireEye discovers breach while investigating
                  intrusion into their network

December 13: SolarWinds and victims notified
December 14: Breach announced publicly - massive scope becomes clear
```

**Impact:**

- 18,000+ organizations compromised
- U.S. Treasury, Commerce, Homeland Security affected
- Estimated $5.4B in global damage
- Critical infrastructure vulnerabilities exposed
- Geopolitical tensions escalated

**Lessons:**

- Supply chain security is critical vulnerability
- Software update integrity must be verified
- Behavioral analytics crucial for detecting C2 communication
- Network segmentation could have limited lateral movement
- Zero-trust security model needed
- Threat hunting can detect dwell time threats

---

## Assessment Activities

### 7.1 Threat Recognition Quiz

**Question 1: Phishing Email Identification**

You receive this email:

```
From: support@amaz0n.com
Subject: URGENT: Verify Your Account

Dear Valued Customer,

We've detected unusual activity on your Amazon account from 
an unrecognized location. To secure your account, please 
verify your information immediately:

Click here to verify: htt p://amazon-verify-account.com/login

This is urgent - click immediately!

Amazon Account Support Team
```

Is this phishing? **YES** - Multiple indicators:
- Domain misspelled (amaz0n, not amazon)
- URL doesn't match sender domain
- Urgency pressure language
- Generic greeting
- Suspicious link format

**Question 2: Social Engineering Scenario**

You receive a call from someone claiming to be from IT:

"Hi, we're doing emergency security updates and need to restart your computer. 
Can you provide your network password so I can validate your account?"

What should you do?

A) Provide your password to expedite the process
B) Hang up and call the IT help desk directly
C) Ask them for their employee ID number
D) Tell them you're too busy right now

**Answer: B** - Never provide credentials over the phone. Always call back to verify.

### 7.2 Threat Response Simulation

**Scenario:**

You notice the following:
- Colleague's account has been sending unusual emails
- Their email is accessing shared drives they don't normally use
- They claim they didn't send those emails

What do you do?

**Correct Response:**

1. **Immediately**: Don't click any links or download attachments
2. **Alert**: Report to security team right away
3. **Document**: Note the emails and unusual activities
4. **Escalate**: Inform your manager
5. **Support**: Assist colleague in securing their account
6. **Investigation**: Allow security team to investigate

**What Not To Do:**

- ❌ Ignore it ("probably just a mistake")
- ❌ Confront colleague publicly
- ❌ Try to investigate yourself
- ❌ Forward the suspicious emails widely
- ❌ Delay reporting

### 7.3 Assessment Rubric

| Competency | Mastered | Proficient | Developing |
|-----------|----------|-----------|-----------|
| **Threat Recognition** | Identifies multiple threat types and attack vectors | Recognizes common threats | Aware of threats but uncertain |
| **Phishing Detection** | Consistently identifies phishing indicators | Catches most obvious phishing | Sometimes misses red flags |
| **Social Engineering Awareness** | Resists manipulation attempts, reports suspicious contact | Generally cautious with requests | May fall for social engineering |
| **Incident Reporting** | Reports incidents promptly with details | Reports incidents appropriately | May delay or under-report |
| **Guardian Utilization** | Leverages Cerberus Guardians for threat detection | Can use Guardians with guidance | Unfamiliar with Guardians |

---

## Summary

This threat awareness training covered:

✅ **Threat Landscape**: Types, actors, motivations
✅ **Attack Scenarios**: APT, ransomware, data breaches
✅ **Social Engineering**: Phishing, pretexting, baiting
✅ **Insider Threats**: Indicators, prevention, detection
✅ **Cerberus Guardians**: Detection and response capabilities
✅ **Real-World Cases**: Target, Equifax, SolarWinds lessons
✅ **Practical Assessment**: Quizzes and scenarios

**Key Takeaways:**

1. Threats are evolving - stay informed
2. Multiple attack vectors - defense in depth required
3. Human element critical - awareness and training essential
4. Detection and response - speed matters
5. Cerberus Guardians provide layered protection
6. Everyone is responsible for security

---

**Document Version**: 1.0
**Last Updated**: 2024
**Training Duration**: 2-3 hours
**Refresh Frequency**: Semi-annually
**Certification Valid For**: 1 year
