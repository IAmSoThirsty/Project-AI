# GitHub Issue: [HIGH] Weak MD5 Hash Usage Without Security Flag (B324) - 4 instances

**Repository:** IAmSoThirsty/Project-AI  
**Labels:** security, high-severity, cryptography

---

## 🔒 Security Vulnerability: Weak MD5 Hash Usage (B324)

### Severity: HIGH

### Summary
Four instances of MD5 hash usage detected without the `usedforsecurity=False` parameter. While these appear to be used for non-cryptographic purposes (cache keys, identifiers), Python 3.9+ requires explicit declaration to comply with FIPS 140-2 and security best practices.

### Vulnerability Details

**Bandit Rule:** B324 - `hashlib.md5()` called without `usedforsecurity` parameter  
**Risk:** Potential security misuse of weak cryptographic hash function  
**Python Version Impact:** Python 3.9+ enforces explicit security context declaration

#### Why MD5 is Weak for Security Contexts
- **Collision Attacks:** MD5 is cryptographically broken; attackers can generate different inputs producing identical hashes
- **Pre-image Attacks:** Feasible to find inputs matching a given hash
- **FIPS Non-Compliance:** MD5 is not FIPS 140-2 approved for cryptographic operations
- **Industry Standards:** NIST deprecated MD5 for security purposes in 2011

### Affected Files (4 instances)

#### 1. `src/app/core/god_tier_intelligence_system.py:571`
**Context:** Cache key generation in intelligent memoization decorator

```python
# VULNERABLE CODE (Line 571)
key = f"{func.__name__}_{hashlib.md5(str((args, kwargs)).encode()).hexdigest()}"
```

**Purpose:** Non-cryptographic cache key generation

---

#### 2. `src/app/core/hydra_50_performance.py:185`
**Context:** Cache key generation in performance optimization

```python
# VULNERABLE CODE (Line 185)
cache_key = hashlib.md5("|".join(key_parts).encode()).hexdigest()
```

**Purpose:** Non-cryptographic cache key generation

---

#### 3. `src/app/core/local_fbo.py:295`
**Context:** Query cache key generation

```python
# VULNERABLE CODE (Lines 295)
def _generate_cache_key(self, query: str) -> str:
    return hashlib.md5(query.lower().strip().encode()).hexdigest()
```

**Purpose:** Non-cryptographic cache key generation

---

#### 4. `src/app/domains/situational_awareness.py:586`
**Context:** Threat contact ID generation

```python
# VULNERABLE CODE (Lines 586-588)
contact_id = hashlib.md5(
    f"{location[0]:.3f},{location[1]:.3f}".encode()
).hexdigest()[:16]
```

**Purpose:** Non-cryptographic contact identifier generation

---

## 🛠️ Recommended Fix

Add `usedforsecurity=False` parameter to all MD5 hash calls used for non-cryptographic purposes.

### Before/After Examples

#### Example 1: god_tier_intelligence_system.py

**BEFORE:**
```python
key = f"{func.__name__}_{hashlib.md5(str((args, kwargs)).encode()).hexdigest()}"
```

**AFTER:**
```python
key = f"{func.__name__}_{hashlib.md5(str((args, kwargs)).encode(), usedforsecurity=False).hexdigest()}"
```

#### Example 2: hydra_50_performance.py

**BEFORE:**
```python
cache_key = hashlib.md5("|".join(key_parts).encode()).hexdigest()
```

**AFTER:**
```python
cache_key = hashlib.md5("|".join(key_parts).encode(), usedforsecurity=False).hexdigest()
```

#### Example 3: local_fbo.py

**BEFORE:**
```python
return hashlib.md5(query.lower().strip().encode()).hexdigest()
```

**AFTER:**
```python
return hashlib.md5(query.lower().strip().encode(), usedforsecurity=False).hexdigest()
```

#### Example 4: situational_awareness.py

**BEFORE:**
```python
contact_id = hashlib.md5(
    f"{location[0]:.3f},{location[1]:.3f}".encode()
).hexdigest()[:16]
```

**AFTER:**
```python
contact_id = hashlib.md5(
    f"{location[0]:.3f},{location[1]:.3f}".encode(),
    usedforsecurity=False
).hexdigest()[:16]
```

---

## ✅ Verification Steps

After applying fixes:

1. **Run Bandit scan:**
   ```bash
   bandit -r src/app/core/god_tier_intelligence_system.py src/app/core/hydra_50_performance.py src/app/core/local_fbo.py src/app/domains/situational_awareness.py -f json
   ```
   
2. **Verify no B324 issues remain:**
   ```bash
   grep -r "B324" bandit-report.json
   ```

3. **Test functionality:**
   - Verify cache operations still work correctly
   - Confirm cache key generation produces consistent results
   - Test threat contact ID generation in situational awareness

4. **Run test suite:**
   ```bash
   pytest tests/ -v
   ```

---

## 📋 Implementation Checklist

- [ ] Fix `src/app/core/god_tier_intelligence_system.py:571`
- [ ] Fix `src/app/core/hydra_50_performance.py:185`
- [ ] Fix `src/app/core/local_fbo.py:295`
- [ ] Fix `src/app/domains/situational_awareness.py:586`
- [ ] Run Bandit security scan
- [ ] Verify no B324 warnings remain
- [ ] Run full test suite
- [ ] Update security documentation

---

## 📚 References

- [Bandit B324 Documentation](https://bandit.readthedocs.io/en/latest/plugins/b324_hashlib.html)
- [Python hashlib Security Considerations](https://docs.python.org/3/library/hashlib.html#hashlib.new)
- [NIST MD5 Deprecation](https://csrc.nist.gov/projects/hash-functions)
- Project Security Report: `SECURITY_VULNERABILITY_ASSESSMENT_REPORT.md`

---

**Note:** All affected usages appear to be for non-cryptographic purposes (cache keys, identifiers). Adding `usedforsecurity=False` explicitly declares this intent and eliminates false-positive security warnings.

---

## 📝 Instructions to Create Issue

To create this issue on GitHub:

### Option 1: Using GitHub CLI (gh)
```bash
gh auth login
gh issue create --repo IAmSoThirsty/Project-AI --title "[HIGH] Weak MD5 Hash Usage Without Security Flag (B324) - 4 instances" --label "security,high-severity,cryptography" --body-file ISSUE_B324_MD5_WEAK_HASH.md
```

### Option 2: Using GitHub Web Interface
1. Navigate to https://github.com/IAmSoThirsty/Project-AI/issues/new
2. Copy the content from this file (excluding this instructions section)
3. Set title: `[HIGH] Weak MD5 Hash Usage Without Security Flag (B324) - 4 instances`
4. Add labels: `security`, `high-severity`, `cryptography`
5. Click "Submit new issue"

### Option 3: Using GitHub API with curl
```bash
curl -X POST \
  -H "Authorization: token YOUR_GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/IAmSoThirsty/Project-AI/issues \
  -d @- <<'EOF'
{
  "title": "[HIGH] Weak MD5 Hash Usage Without Security Flag (B324) - 4 instances",
  "body": "...(paste full body here)...",
  "labels": ["security", "high-severity", "cryptography"]
}
EOF
```
