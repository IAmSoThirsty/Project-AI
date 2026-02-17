# Governance Decision Flow - Triumvirate Architecture

## Overview

The Governance Decision Flow implements a three-layer hierarchical decision-making system that validates all operations against ethical, security, and policy requirements. This architecture ensures that Project-AI operates within defined boundaries while maintaining transparency and accountability.

## The Triumvirate Architecture

```
                    ┌──────────────────────────────────┐
                    │   GOVERNANCE TRIUMVIRATE         │
                    │                                  │
                    │  Sequential Validation Chain     │
                    │  Unanimous Approval Required     │
                    └──────────────────────────────────┘
                                   │
                                   ↓
        ┌──────────────────────────┼──────────────────────────┐
        │                          │                          │
        ↓                          ↓                          ↓
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│    GALAHAD       │    │    CERBERUS      │    │ CODEX DEUS MAX   │
│  (Ethics Layer)  │───→│ (Security Layer) │───→│  (Policy Layer)  │
│                  │    │                  │    │                  │
│ • Asimov's Laws  │    │ • Threat Detect  │    │ • Org Policies   │
│ • Harm Detection │    │ • Injection Prev │    │ • Compliance     │
│ • Human Authority│    │ • PII Protection │    │ • Business Rules │
│ • Escalation     │    │ • Abuse Pattern  │    │ • Final Authority│
└──────────────────┘    └──────────────────┘    └──────────────────┘
        │                          │                          │
        └──────────────────────────┼──────────────────────────┘
                                   │
                    ANY REJECTION = REQUEST REJECTED
                    ALL APPROVED = REQUEST APPROVED
                                   │
                                   ↓
                    ┌──────────────────────────────────┐
                    │      FINAL DECISION              │
                    │                                  │
                    │  • Approval Hash Generation      │
                    │  • Audit Trail Recording         │
                    │  • Execution Authorization       │
                    └──────────────────────────────────┘
```

## Sequential Validation Process

### Layer 1: Galahad (Ethics Validation)

**Purpose**: Ensure all operations comply with Asimov's Laws and ethical guidelines.

**Core Responsibilities**:

1. Validate against hierarchical laws (0→1→2→3)
1. Detect potential harm to humans or humanity
1. Verify human authority and permissions
1. Escalate ambiguous cases to human oversight

**Decision Logic**:

```python
class Galahad:
    """Ethics validation layer implementing Asimov's Laws."""

    # Hierarchical laws (0 is highest priority)

    LAWS = OrderedDict([
        ('law_0', {
            'text': 'A robot may not harm humanity, or allow humanity to come to harm',
            'priority': 0,
            'scope': 'existential'
        }),
        ('law_1', {
            'text': 'A robot may not injure a human or allow a human to come to harm',
            'priority': 1,
            'scope': 'individual'
        }),
        ('law_2', {
            'text': 'A robot must obey human orders except when in conflict with Laws 0-1',
            'priority': 2,
            'scope': 'obedience'
        }),
        ('law_3', {
            'text': 'A robot must protect its own existence except when in conflict with Laws 0-2',
            'priority': 3,
            'scope': 'self_preservation'
        })
    ])

    def validate(self, request: EnrichedRequest) -> GalahadDecision:
        """
        Validate request against Asimov's Laws.

        Returns:
            GalahadDecision with approved/rejected status and rationale
        """

        # Check Law 0: Humanity-level harm

        if self._check_existential_threat(request):
            return GalahadDecision(
                approved=False,
                law_violated='law_0',
                reason='Request poses existential risk to humanity',
                severity='CRITICAL',
                escalate_to_human=True,
                rationale=self._generate_rationale(request, 'law_0')
            )

        # Check Law 1: Individual harm

        harm_assessment = self._assess_individual_harm(request)
        if harm_assessment.harm_detected:
            return GalahadDecision(
                approved=False,
                law_violated='law_1',
                reason=f'Request may cause harm: {harm_assessment.description}',
                severity=harm_assessment.severity,
                affected_parties=harm_assessment.affected_users,
                rationale=self._generate_rationale(request, 'law_1')
            )

        # Check Law 2: Human authority validation

        authority_check = self._validate_human_authority(request)
        if not authority_check.authorized:
            if authority_check.escalation_required:
                return GalahadDecision(
                    approved=False,
                    law_violated='law_2',
                    reason='Insufficient authority, escalation required',
                    severity='MEDIUM',
                    escalate_to_human=True,
                    escalation_reason=authority_check.escalation_reason,
                    rationale=self._generate_rationale(request, 'law_2')
                )
            else:
                return GalahadDecision(
                    approved=False,
                    law_violated='law_2',
                    reason='Human order cannot be validated',
                    severity='HIGH',
                    rationale=self._generate_rationale(request, 'law_2')
                )

        # Check Law 3: Self-preservation (only if no conflicts)

        if self._threatens_system_integrity(request):
            return GalahadDecision(
                approved=False,
                law_violated='law_3',
                reason='Request threatens system integrity',
                severity='MEDIUM',
                requires_override=True,
                rationale=self._generate_rationale(request, 'law_3')
            )

        # All checks passed

        return GalahadDecision(
            approved=True,
            reason='All ethical validations passed',
            confidence=self._calculate_confidence(request),
            rationale=self._generate_approval_rationale(request)
        )

    def _check_existential_threat(self, request: EnrichedRequest) -> bool:
        """Detect if request poses existential risk to humanity."""
        threat_patterns = [
            r'(?i)(nuclear|biological|chemical)\s+(weapon|attack)',
            r'(?i)genocide|mass\s+extinction',
            r'(?i)destroy\s+(humanity|civilization|world)',
            r'(?i)AI\s+(takeover|uprising|rebellion)',
            r'(?i)pandemic|bioterrorism'
        ]

        content = request.content.lower()
        for pattern in threat_patterns:
            if re.search(pattern, content):
                return True

        # ML-based threat detection

        threat_score = self.threat_classifier.predict_proba(request.content)[0][1]
        return threat_score > 0.9  # 90% confidence threshold

    def _assess_individual_harm(self, request: EnrichedRequest) -> HarmAssessment:
        """Assess potential harm to individuals."""
        harm_indicators = {
            'physical': [
                r'(?i)(kill|harm|hurt|injure|attack)',
                r'(?i)(poison|drug|overdose)',
                r'(?i)(suicide|self[-\s]harm)'
            ],
            'psychological': [
                r'(?i)(blackmail|extort|threaten)',
                r'(?i)(harass|stalk|intimidate)',
                r'(?i)(doxx|expose\s+personal)'
            ],
            'financial': [
                r'(?i)(steal|fraud|embezzle)',
                r'(?i)(scam|phish|ransomware)',
                r'(?i)(money\s+launder|tax\s+evasion)'
            ],
            'privacy': [
                r'(?i)(spy|surveil|monitor\s+secretly)',
                r'(?i)(leak|expose)\s+.*(data|password|secret)',
                r'(?i)unauthorized\s+access'
            ]
        }

        detected_harms = []
        for category, patterns in harm_indicators.items():
            for pattern in patterns:
                if re.search(pattern, request.content):
                    detected_harms.append({
                        'category': category,
                        'pattern': pattern,
                        'confidence': 0.8
                    })

        if detected_harms:
            return HarmAssessment(
                harm_detected=True,
                description=f"Detected {len(detected_harms)} harm indicators",
                severity='HIGH' if len(detected_harms) > 2 else 'MEDIUM',
                categories=[h['category'] for h in detected_harms],
                affected_users=self._identify_affected_users(request)
            )

        return HarmAssessment(harm_detected=False)

    def _validate_human_authority(self, request: EnrichedRequest) -> AuthorityCheck:
        """Validate that request comes from authorized human."""
        user = request.context['user_profile']

        # Check if user is authenticated human (not bot)

        if user.get('is_bot', False):
            return AuthorityCheck(
                authorized=False,
                reason='Requests must come from authenticated humans'
            )

        # Check security clearance level

        required_clearance = self._determine_required_clearance(request)
        user_clearance = user.get('security_clearance', 0)

        if user_clearance < required_clearance:
            return AuthorityCheck(
                authorized=False,
                escalation_required=True,
                escalation_reason=f'Required clearance: {required_clearance}, User has: {user_clearance}',
                required_clearance=required_clearance,
                user_clearance=user_clearance
            )

        # Check for special permissions

        if self._requires_special_permission(request):
            if not self._has_special_permission(user, request):
                return AuthorityCheck(
                    authorized=False,
                    escalation_required=True,
                    escalation_reason='Special permission required',
                    required_permission=self._get_required_permission(request)
                )

        return AuthorityCheck(authorized=True)

    def _threatens_system_integrity(self, request: EnrichedRequest) -> bool:
        """Check if request threatens system's ability to function."""
        threat_patterns = [
            r'(?i)(shutdown|terminate|kill)\s+(system|process|server)',
            r'(?i)delete\s+(database|all\s+data|system\s+files)',
            r'(?i)(disable|remove)\s+(security|authentication|audit)',
            r'(?i)format\s+(disk|drive|volume)',
            r'(?i)(corrupt|destroy)\s+(memory|storage|backup)'
        ]

        # Check if request would disable critical functions

        critical_functions = ['governance', 'audit', 'memory', 'authentication']
        for func in critical_functions:
            if re.search(rf'(?i)disable.*{func}', request.content):
                return True

        return any(re.search(pattern, request.content) for pattern in threat_patterns)

    def _generate_rationale(self, request: EnrichedRequest, law_violated: str) -> str:
        """Generate human-readable rationale for decision."""
        law = self.LAWS[law_violated]

        rationale = f"""
        ETHICS DECISION RATIONALE

        Law Violated: {law_violated}
        Law Text: {law['text']}
        Priority: {law['priority']} (0 = highest)
        Scope: {law['scope']}

        Request Analysis:

        - User: {request.context['user_profile']['name']}
        - Intent: {request.intent.intent}
        - Content: {request.content[:200]}...

        Decision: REJECTED
        Reason: This request violates {law_violated} which is fundamental to ethical operation.

        The system is designed to prioritize {law['scope']}-level considerations.
        Alternative approaches that don't violate this law should be explored.

        If you believe this is an error, please escalate to human oversight.
        """

        return rationale.strip()
```

**Decision Matrix**:

| Request Type                        | Galahad Decision | Rationale                 |
| ----------------------------------- | ---------------- | ------------------------- |
| "Delete my account"                 | APPROVE          | User autonomy (Law 2)     |
| "Show me John's password"           | REJECT           | Privacy violation (Law 1) |
| "Shutdown the system"               | REJECT           | Self-preservation (Law 3) |
| "Execute arbitrary code"            | REJECT           | Security risk (Law 1)     |
| "Generate hate speech"              | REJECT           | Potential harm (Law 1)    |
| "Help me with homework"             | APPROVE          | No harm detected          |
| "Scan for security vulnerabilities" | APPROVE          | Protective action         |
| "Delete another user's data"        | REJECT           | Unauthorized (Law 2)      |

**Performance**: < 30ms per validation (rule-based + ML classifier)

### Layer 2: Cerberus (Security Validation)

**Purpose**: Protect against security threats and malicious activities.

**Core Responsibilities**:

1. Detect injection attacks (SQL, command, code)
1. Prevent sensitive data exposure
1. Identify abuse patterns
1. Enforce security policies

**Decision Logic**:

```python
class Cerberus:
    """Security validation layer implementing threat detection."""

    def validate(self, request: EnrichedRequest, galahad_result: GalahadDecision) -> CerberusDecision:
        """
        Validate request against security policies.

        Args:
            request: The enriched request to validate
            galahad_result: Result from Galahad ethics validation

        Returns:
            CerberusDecision with security assessment
        """

        # If Galahad rejected, skip security validation

        if not galahad_result.approved:
            return CerberusDecision(
                approved=False,
                reason='Galahad pre-rejection',
                skip_validation=True
            )

        security_checks = []

        # Check 1: SQL Injection

        sql_check = self._check_sql_injection(request)
        security_checks.append(sql_check)
        if sql_check.threat_detected:
            return self._create_rejection(
                'SQL injection attempt detected',
                sql_check,
                incident_type='injection_attack'
            )

        # Check 2: Command Injection

        cmd_check = self._check_command_injection(request)
        security_checks.append(cmd_check)
        if cmd_check.threat_detected:
            return self._create_rejection(
                'Command injection attempt detected',
                cmd_check,
                incident_type='injection_attack'
            )

        # Check 3: Cross-Site Scripting (XSS)

        xss_check = self._check_xss(request)
        security_checks.append(xss_check)
        if xss_check.threat_detected:
            return self._create_rejection(
                'XSS attack attempt detected',
                xss_check,
                incident_type='injection_attack'
            )

        # Check 4: Path Traversal

        path_check = self._check_path_traversal(request)
        security_checks.append(path_check)
        if path_check.threat_detected:
            return self._create_rejection(
                'Path traversal attempt detected',
                path_check,
                incident_type='unauthorized_access'
            )

        # Check 5: Sensitive Data Exposure

        pii_check = self._check_pii_exposure(request)
        security_checks.append(pii_check)
        if pii_check.threat_detected:
            return self._create_rejection(
                'Request would expose PII',
                pii_check,
                incident_type='data_exposure',
                compliance_violation='GDPR'
            )

        # Check 6: Secrets Detection

        secrets_check = self._check_secrets(request)
        security_checks.append(secrets_check)
        if secrets_check.threat_detected:
            return self._create_rejection(
                'Secrets detected in request',
                secrets_check,
                incident_type='secrets_exposure'
            )

        # Check 7: SSRF (Server-Side Request Forgery)

        ssrf_check = self._check_ssrf(request)
        security_checks.append(ssrf_check)
        if ssrf_check.threat_detected:
            return self._create_rejection(
                'SSRF attempt detected',
                ssrf_check,
                incident_type='ssrf_attack'
            )

        # Check 8: Abuse Pattern Detection

        abuse_check = self._check_abuse_patterns(request)
        security_checks.append(abuse_check)
        if abuse_check.threat_detected:
            return self._create_rejection(
                'Abuse pattern detected',
                abuse_check,
                incident_type='abuse',
                action='flag_account'
            )

        # Check 9: Authentication Bypass

        auth_check = self._check_authentication_bypass(request)
        security_checks.append(auth_check)
        if auth_check.threat_detected:
            return self._create_rejection(
                'Authentication bypass attempt',
                auth_check,
                incident_type='auth_bypass'
            )

        # Check 10: Authorization Violations

        authz_check = self._check_authorization(request)
        security_checks.append(authz_check)
        if authz_check.threat_detected:
            return self._create_rejection(
                'Authorization violation',
                authz_check,
                incident_type='authz_violation'
            )

        # All security checks passed

        return CerberusDecision(
            approved=True,
            reason='All security validations passed',
            security_score=self._calculate_security_score(security_checks),
            checks_performed=len(security_checks),
            confidence=0.95
        )

    def _check_sql_injection(self, request: EnrichedRequest) -> SecurityCheck:
        """Detect SQL injection attempts."""
        sql_patterns = [
            r"(?i)(\s|^)(union|select|insert|update|delete|drop|create|alter|exec|execute)(\s|$)",
            r"(?i)(;|\-\-|\/\*).*(\s|^)(select|union|insert|update|delete)",
            r"(?i)(or|and)\s+\d+\s*=\s*\d+",
            r"(?i)(or|and)\s+['\"].*['\"]\s*=\s*['\"]",
            r"(?i)(exec|execute)\s*\(",
            r"(?i)xp_cmdshell",
            r"(?i)(information_schema|sysobjects|syscolumns)"
        ]

        content = request.content
        detected_patterns = []

        for pattern in sql_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                detected_patterns.append({
                    'pattern': pattern,
                    'match': match.group(),
                    'position': match.span()
                })

        if detected_patterns:
            return SecurityCheck(
                check_name='sql_injection',
                threat_detected=True,
                severity='CRITICAL',
                details=detected_patterns,
                recommendation='Sanitize input and use parameterized queries'
            )

        return SecurityCheck(
            check_name='sql_injection',
            threat_detected=False
        )

    def _check_command_injection(self, request: EnrichedRequest) -> SecurityCheck:
        """Detect command injection attempts."""
        cmd_patterns = [
            r"(?i)(;|\||&|`|\$\(|\$\{).*(\s|^)(ls|cat|rm|chmod|wget|curl|nc|bash|sh|python|perl)",
            r"(?i)(\|\||&&).*(\s|^)(rm|del|format|shutdown)",
            r"(?i)>\s*/dev/(null|zero|random)",
            r"(?i)</.*>",  # Process substitution
            r"(?i)\$\{.*\}",  # Variable expansion
            r"(?i)`.*`"  # Command substitution
        ]

        content = request.content
        detected_patterns = []

        for pattern in cmd_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                detected_patterns.append({
                    'pattern': pattern,
                    'match': match.group(),
                    'position': match.span()
                })

        if detected_patterns:
            return SecurityCheck(
                check_name='command_injection',
                threat_detected=True,
                severity='CRITICAL',
                details=detected_patterns,
                recommendation='Never pass user input directly to shell commands'
            )

        return SecurityCheck(
            check_name='command_injection',
            threat_detected=False
        )

    def _check_pii_exposure(self, request: EnrichedRequest) -> SecurityCheck:
        """Check if request would expose PII."""

        # Check if request asks for sensitive fields

        sensitive_fields = [
            'password', 'ssn', 'social_security',
            'credit_card', 'bank_account',
            'api_key', 'secret', 'token',
            'private_key', 'certificate'
        ]

        content_lower = request.content.lower()
        exposed_fields = [
            field for field in sensitive_fields
            if field in content_lower
        ]

        if exposed_fields:

            # Check if user has permission to access these fields

            user_clearance = request.context['user_profile'].get('security_clearance', 0)
            required_clearance = 5  # PII access requires clearance level 5

            if user_clearance < required_clearance:
                return SecurityCheck(
                    check_name='pii_exposure',
                    threat_detected=True,
                    severity='HIGH',
                    details={
                        'exposed_fields': exposed_fields,
                        'required_clearance': required_clearance,
                        'user_clearance': user_clearance
                    },
                    compliance_violation='GDPR, HIPAA',
                    recommendation='Request must be from authorized personnel'
                )

        return SecurityCheck(
            check_name='pii_exposure',
            threat_detected=False
        )

    def _check_abuse_patterns(self, request: EnrichedRequest) -> SecurityCheck:
        """Detect abuse patterns (rapid requests, scripted behavior)."""
        user_id = request.context['user_profile']['id']

        # Get recent request history

        recent_requests = self._get_recent_requests(user_id, minutes=5)

        # Check for rapid-fire requests

        if len(recent_requests) > 50:  # > 50 requests in 5 minutes
            return SecurityCheck(
                check_name='abuse_pattern',
                threat_detected=True,
                severity='MEDIUM',
                details={
                    'pattern': 'rapid_requests',
                    'count': len(recent_requests),
                    'threshold': 50,
                    'window': '5 minutes'
                },
                recommendation='Flag account for review, temporary rate limit'
            )

        # Check for identical requests (copy-paste attack)

        if self._detect_duplicate_requests(recent_requests, threshold=10):
            return SecurityCheck(
                check_name='abuse_pattern',
                threat_detected=True,
                severity='MEDIUM',
                details={
                    'pattern': 'duplicate_requests',
                    'threshold': 10
                },
                recommendation='Possible bot activity, require CAPTCHA'
            )

        # Check for unusual time patterns

        if self._detect_unusual_timing(recent_requests):
            return SecurityCheck(
                check_name='abuse_pattern',
                threat_detected=True,
                severity='LOW',
                details={
                    'pattern': 'unusual_timing',
                    'description': 'Requests at precise intervals (bot-like)'
                },
                recommendation='Monitor account activity'
            )

        return SecurityCheck(
            check_name='abuse_pattern',
            threat_detected=False
        )
```

**Threat Categories**:

1. **Injection Attacks** (CRITICAL):

   - SQL injection
   - Command injection
   - Code injection
   - XSS (Cross-Site Scripting)

1. **Data Exposure** (HIGH):

   - PII leakage
   - Secrets exposure
   - Unauthorized data access

1. **Infrastructure Attacks** (CRITICAL):

   - SSRF (Server-Side Request Forgery)
   - Path traversal
   - Directory listing

1. **Authentication/Authorization** (HIGH):

   - Authentication bypass
   - Privilege escalation
   - Session hijacking

1. **Abuse Patterns** (MEDIUM):

   - Rapid-fire requests
   - Duplicate requests
   - Scraping behavior

**Performance**: < 40ms per validation (regex + database lookups)

### Layer 3: Codex Deus Maximus (Policy Validation)

**Purpose**: Enforce organizational policies, compliance, and business rules.

**Core Responsibilities**:

1. Validate against organizational policies
1. Ensure regulatory compliance (GDPR, HIPAA, SOC2)
1. Apply business rules
1. Make final approval/rejection decision

**Decision Logic**:

```python
class CodexDeusMaximus:
    """Final authority for policy enforcement and compliance."""

    def validate(self, request: EnrichedRequest, galahad_result: GalahadDecision,
                 cerberus_result: CerberusDecision) -> FinalDecision:
        """
        Make final governance decision after ethics and security validation.

        Args:
            request: The enriched request
            galahad_result: Ethics validation result
            cerberus_result: Security validation result

        Returns:
            FinalDecision with approval/rejection and rationale
        """

        # Check if previous layers rejected

        if not galahad_result.approved:
            return FinalDecision(
                approved=False,
                reason=f"Ethics rejection: {galahad_result.reason}",
                governance_layer='galahad',
                rejection_details=galahad_result
            )

        if not cerberus_result.approved:
            return FinalDecision(
                approved=False,
                reason=f"Security rejection: {cerberus_result.reason}",
                governance_layer='cerberus',
                rejection_details=cerberus_result,
                security_incident=cerberus_result.security_incident
            )

        # Apply organizational policies

        policy_check = self._check_organizational_policies(request)
        if not policy_check.compliant:
            return FinalDecision(
                approved=False,
                reason=f"Policy violation: {policy_check.violated_policy}",
                governance_layer='codex',
                policy_details=policy_check
            )

        # Check regulatory compliance

        compliance_check = self._check_compliance(request)
        if not compliance_check.compliant:
            return FinalDecision(
                approved=False,
                reason=f"Compliance violation: {compliance_check.regulation}",
                governance_layer='codex',
                compliance_details=compliance_check
            )

        # Apply business rules

        business_check = self._check_business_rules(request)
        if not business_check.compliant:
            return FinalDecision(
                approved=False,
                reason=f"Business rule violation: {business_check.rule}",
                governance_layer='codex',
                business_details=business_check
            )

        # Check resource limits

        resource_check = self._check_resource_limits(request)
        if not resource_check.within_limits:
            return FinalDecision(
                approved=False,
                reason=f"Resource limit exceeded: {resource_check.limit_type}",
                governance_layer='codex',
                resource_details=resource_check
            )

        # Final approval

        approval_hash = self._generate_approval_hash(
            request, galahad_result, cerberus_result
        )

        return FinalDecision(
            approved=True,
            reason="All governance validations passed",
            governance_layers_approved=['galahad', 'cerberus', 'codex'],
            approval_hash=approval_hash,
            approval_timestamp=datetime.utcnow(),
            valid_for_seconds=300,  # Approval valid for 5 minutes
            metadata={
                'ethics_confidence': galahad_result.confidence,
                'security_score': cerberus_result.security_score,
                'policy_compliance': True,
                'regulatory_compliance': True
            }
        )

    def _generate_approval_hash(self, request: EnrichedRequest,
                                galahad: GalahadDecision,
                                cerberus: CerberusDecision) -> str:
        """Generate cryptographic hash of approval decision."""
        approval_data = {
            'request_id': request.id,
            'user_id': request.user_id,
            'intent': request.intent.intent,
            'content_hash': hashlib.sha256(request.content.encode()).hexdigest(),
            'galahad_approved': galahad.approved,
            'cerberus_approved': cerberus.approved,
            'timestamp': datetime.utcnow().isoformat()
        }

        return hashlib.sha256(
            json.dumps(approval_data, sort_keys=True).encode()
        ).hexdigest()
```

**Policy Categories**:

1. **Data Retention Policies**:

   - Hot storage: 90 days
   - Warm storage: 7 years
   - Permanent: audit trail

1. **Access Control Policies**:

   - RBAC enforcement
   - Least privilege principle
   - Separation of duties

1. **Compliance Policies**:

   - GDPR: consent, right to deletion
   - HIPAA: PHI protection
   - SOC2: audit trail completeness

1. **Business Rules**:

   - Resource quotas per user
   - Feature flags
   - Geographic restrictions

1. **Operational Policies**:

   - Maintenance windows
   - Blackout periods
   - Disaster recovery

**Performance**: < 30ms per validation (policy engine with cached rules)

## Decision Outcomes

### Unanimous Approval Required

```python
def make_final_decision(galahad: GalahadDecision,
                       cerberus: CerberusDecision,
                       codex: FinalDecision) -> GovernanceDecision:
    """
    Combine all three governance decisions.
    ALL must approve for execution to proceed.
    """
    if not (galahad.approved and cerberus.approved and codex.approved):

        # Find first rejection

        rejecting_layer = (
            'galahad' if not galahad.approved else
            'cerberus' if not cerberus.approved else
            'codex'
        )

        return GovernanceDecision(
            approved=False,
            rejecting_layer=rejecting_layer,
            reason=get_rejection_reason(galahad, cerberus, codex),
            timestamp=datetime.utcnow()
        )

    # All approved

    return GovernanceDecision(
        approved=True,
        approval_hash=codex.approval_hash,
        governance_chain=[galahad, cerberus, codex],
        timestamp=datetime.utcnow(),
        valid_until=datetime.utcnow() + timedelta(seconds=300)
    )
```

### Rejection Handling

```python
def handle_rejection(decision: GovernanceDecision, request: EnrichedRequest):
    """Handle rejected requests with appropriate actions."""

    # Record rejection in memory

    await memory_engine.record(
        channel='decision',
        operation_id=request.id,
        data={
            'decision': 'REJECTED',
            'rejecting_layer': decision.rejecting_layer,
            'reason': decision.reason,
            'timestamp': decision.timestamp
        }
    )

    # Record in audit trail

    await audit_trail.record_rejection(
        request_id=request.id,
        user_id=request.user_id,
        governance_decision=decision
    )

    # Handle security incidents

    if decision.security_incident:
        await security_incident_handler.report(
            user_id=request.user_id,
            incident_type=decision.incident_type,
            details=decision.rejection_details
        )

    # Check if escalation is required

    if decision.requires_escalation:
        await escalation_service.escalate_to_human(
            request=request,
            decision=decision,
            priority=decision.escalation_priority
        )

    # Return error response to user

    return create_rejection_response(decision)
```

## Governance Metrics

### Performance Targets (P95)

- Galahad validation: < 30ms
- Cerberus validation: < 40ms
- Codex validation: < 30ms
- **Total governance time: < 100ms**

### Decision Statistics

- Approval rate: 95-98% (expected)
- Galahad rejections: 1-2%
- Cerberus rejections: 0.5-1%
- Codex rejections: 0.5-1%
- Security incidents: < 0.1%

### Monitoring

```python

# Prometheus metrics

governance_decisions_total = Counter(
    'governance_decisions_total',
    'Total governance decisions',
    ['layer', 'decision']
)

governance_duration_seconds = Histogram(
    'governance_duration_seconds',
    'Governance validation duration',
    ['layer']
)

governance_rejections_total = Counter(
    'governance_rejections_total',
    'Total governance rejections',
    ['layer', 'reason']
)

security_incidents_total = Counter(
    'security_incidents_total',
    'Total security incidents',
    ['incident_type']
)
```

## Audit Trail Recording

Every governance decision is recorded in the immutable audit trail:

```python
def record_governance_decision(request: EnrichedRequest,
                               galahad: GalahadDecision,
                               cerberus: CerberusDecision,
                               codex: FinalDecision):
    """Record complete governance decision in audit trail."""

    audit_entry = {
        'event_type': 'governance_decision',
        'request_id': request.id,
        'user_id': request.user_id,
        'timestamp': datetime.utcnow().isoformat(),
        'governance_chain': {
            'galahad': {
                'approved': galahad.approved,
                'reason': galahad.reason,
                'confidence': galahad.confidence,
                'law_violated': galahad.law_violated if not galahad.approved else None
            },
            'cerberus': {
                'approved': cerberus.approved,
                'reason': cerberus.reason,
                'security_score': cerberus.security_score,
                'security_incident': cerberus.security_incident
            },
            'codex': {
                'approved': codex.approved,
                'reason': codex.reason,
                'approval_hash': codex.approval_hash if codex.approved else None
            }
        },
        'final_decision': codex.approved,
        'approval_hash': codex.approval_hash if codex.approved else None
    }

    # Add to hash chain

    previous_hash = get_latest_audit_hash()
    audit_entry['previous_hash'] = previous_hash

    current_hash = hashlib.sha256(
        json.dumps(audit_entry, sort_keys=True).encode()
    ).hexdigest()
    audit_entry['current_hash'] = current_hash

    # Append to immutable log

    audit_trail.append(audit_entry)

    return current_hash
```

## Human Escalation

Some cases require human oversight:

```python
def check_escalation_required(galahad: GalahadDecision,
                              cerberus: CerberusDecision,
                              codex: FinalDecision) -> bool:
    """Determine if human escalation is required."""

    escalation_triggers = [
        galahad.escalate_to_human,
        cerberus.severity == 'CRITICAL' and not cerberus.approved,
        codex.compliance_violation is not None,
        galahad.confidence < 0.7,  # Low confidence in ethics decision
        cerberus.security_score < 0.5  # Low security score
    ]

    return any(escalation_triggers)

async def escalate_to_human(request: EnrichedRequest,
                            governance_results: GovernanceResults):
    """Escalate decision to human oversight team."""

    escalation = {
        'request_id': request.id,
        'user_id': request.user_id,
        'timestamp': datetime.utcnow(),
        'priority': determine_priority(governance_results),
        'summary': generate_escalation_summary(request, governance_results),
        'governance_chain': governance_results,
        'recommended_action': suggest_action(governance_results)
    }

    # Notify oversight team

    await notification_service.notify_oversight_team(escalation)

    # Store in escalation queue

    await escalation_queue.add(escalation)

    # Return pending status to user

    return PendingReviewResponse(
        message="Your request requires human review",
        escalation_id=escalation['request_id'],
        estimated_review_time="24 hours"
    )
```

## Related Documentation

- [User Request Flow](./user_request_flow.md)
- [Memory Recording Flow](./memory_recording_flow.md)
- [Audit Trail Flow](./audit_trail_flow.md)
- [Security Architecture](../security/README.md)
