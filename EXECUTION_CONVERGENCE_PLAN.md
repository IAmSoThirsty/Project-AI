---
type: plan
tags:
  - p2-root
  - status
  - plan
  - governance
  - execution-convergence
  - desktop-integration
created: 2026-04-13
last_verified: 2026-04-20
status: archived
related_systems:
  - governance-pipeline
  - desktop-gui
  - dashboard-main
stakeholders:
  - governance-team
  - desktop-team
report_type: plan
supersedes: []
review_cycle: as-needed
---

# Execution Path Convergence - The Real Fix

**Discovery**: Desktop adapter IS injected, routing methods EXIST, but **never called**

---

## 🎯 The Execution Spine (Found)

### Current Flow (BYPASS)
```
Button Click → Signal → Handler Method → Direct Core Call
                                       ↓
                              self.lrm.approve_request()
                              self.kernel.execute()
                              self.codex.fix_repo()
```

### Target Flow (GOVERNED)
```
Button Click → Signal → Handler Method → _route_through_governance()
                                       ↓
                              desktop_adapter.execute()
                                       ↓
                              route_request("desktop", ...)
                                       ↓
                              enforce_pipeline()
```

---

## 📍 Central Dispatch Layer Found

**File**: `src/app/gui/dashboard_main.py`

**Key Methods**:
- Line 442: `set_desktop_adapter()` - ✅ Adapter injection (WORKS)
- Line 451: `_route_through_governance()` - ✅ Routing method (EXISTS BUT UNUSED)

**Handler Methods** (the spine):
- Line 91: `approve_selected()` - Calls `self.lrm.approve_request()` directly
- Line 92: `deny_selected()` - Calls `self.lrm.deny_request()` directly  
- Line 220: `run_codex_fix()` - Calls `self.codex_adapter.codex.fix_repo()` directly
- Line 337: `activate_selected()` - Calls `self.codex_adapter.codex.activate_staged()` directly

**Pattern**: Infrastructure exists, just not wired to handlers

---

## 🔧 The Fix (5-15 Integration Points, Not 345)

### Phase 1: Wire Existing Infrastructure

Transform handlers from:
```python
def approve_selected(self):
    sel = self.pending_list.currentItem()
    if not sel:
        return
    sel_id = sel.text().split(":")[0]
    ok = self.lrm.approve_request(sel_id, response="Approved via Dashboard")  # DIRECT
    if ok:
        QMessageBox.information(self, "Approved", f"Request {sel_id} approved")
```

To:
```python
def approve_selected(self):
    sel = self.pending_list.currentItem()
    if not sel:
        return
    sel_id = sel.text().split(":")[0]
    
    # ROUTE THROUGH GOVERNANCE
    result = self._route_through_governance("learning.approve", {
        "request_id": sel_id,
        "response": "Approved via Dashboard"
    })
    
    if result.get("status") == "fallback":
        # Fallback to direct call if adapter unavailable
        ok = self.lrm.approve_request(sel_id, response="Approved via Dashboard")
    else:
        ok = result.get("success", False)
    
    if ok:
        QMessageBox.information(self, "Approved", f"Request {sel_id} approved")
```

**Change**: 3 lines added, 1 line modified per handler  
**Safety**: Graceful fallback if adapter missing  
**Coverage**: Each modified handler = 1-20 GUI methods governed

---

## 📋 Target Handler Methods (Convergence Points)

### dashboard_main.py (8 handlers)
1. `approve_selected()` → `learning.approve`
2. `deny_selected()` → `learning.deny`
3. `run_codex_fix()` → `codex.fix`
4. `activate_selected()` → `codex.activate`
5. `run_qa_on_selected()` → `codex.qa`
6. `grant_integrator()` → `access.grant`
7. `export_audit()` → `audit.export`
8. `toggle_agents()` → `agents.toggle`

### dashboard.py (11 handlers - if using LeatherBook UI)
1. `send_message()` → `ai.chat`
2. `add_task()` → `persona.task`
3. `generate_learning_path()` → `learning.generate`
4. `perform_analysis()` → `data.analyze`
5. `add_security_favorite()` → `security.favorite`
6. `toggle_location_tracking()` → `location.toggle`
7. `clear_location_history()` → `location.clear`
8. `save_emergency_contacts()` → `emergency.save`
9. `send_emergency_alert()` → `emergency.alert`
10. `load_data_file()` → `data.load`
11. `open_settings_dialog()` → `settings.open`

### Other panels (estimated 10-15 additional convergence points)
- `god_tier_panel.py`: `generate_assessment()` → `assessment.generate`
- `cerberus_panel.py`: `_tag_selected()`, `_release_selected()` → cerberus actions
- `hydra_50_panel.py`: Scenario/alert actions
- `image_generation.py`: `_on_generate()` → `ai.image`
- `persona_panel.py`: `test_action()`, `reset_personality()` → persona actions
- `user_management.py`: CRUD operations → user actions

**Total Convergence Points**: ~30-35 handler methods  
**Not**: 345 individual methods

---

## 🚨 The Dual Governance Problem

### Current State
**System A**: Runtime Router (Web/CLI)
```
Web → route_request() → enforce_pipeline() → orchestrator → systems
```

**System B**: CognitionKernel (Agents)
```
Agents → kernel.execute() → agent governance → systems
```

**Problem**: Desktop GUI could use EITHER, currently uses NEITHER

### Solution Options

#### Option 1: Desktop → Runtime Router (Recommended)
```python
# In dashboard handlers
result = self._route_through_governance("action", payload)
    ↓
desktop_adapter.execute()
    ↓
route_request("desktop", ...)
    ↓
enforce_pipeline()
    ↓
Core systems
```

**Pros**: 
- Infrastructure already exists
- Consistent with Web/CLI
- Agent integration done as separate layer

**Cons**:
- CognitionKernel remains separate (acceptable - agents already governed)

#### Option 2: Unify Router + Kernel (Future Epic)
```python
# Enhanced router that integrates kernel
route_request() → enforce_pipeline() → {
    if agent_action: kernel.execute()
    elif ai_action: orchestrator.run_ai()
    else: core_system_call()
}
```

**Pros**: True unification  
**Cons**: Large refactor, not needed for Level 2

**Decision**: Use Option 1 for Level 2, Option 2 as future enhancement

---

## 📊 Implementation Metrics

### Current Bypass Rate
- GUI methods: 345
- Calling route_request(): 0
- Bypass rate: **100%**

### Target Convergence (after fix)
- GUI methods: 345
- Convergence points modified: ~30-35
- Methods routed: 345 (all flow through convergence points)
- Bypass rate: **0%**

### Implementation Effort
| Task | Effort | Impact |
|------|--------|--------|
| Wire dashboard_main.py handlers | 2 hours | ~50 methods governed |
| Wire dashboard.py handlers | 2 hours | ~100 methods governed |
| Wire panel handlers | 3 hours | ~150 methods governed |
| Test integration | 1 hour | Verify no breakage |
| **TOTAL** | **8 hours** | **345 methods governed** |

Compare to: Patching 345 methods individually = 40+ hours

---

## 🎯 Success Criteria

### Before
```bash
grep -r "route_request" src/app/gui/*.py
# Result: 0 matches
```

### After
```bash
grep -r "route_request" src/app/gui/*.py
# Result: 30-35 matches in handler methods
```

### Verification
```python
# Test script
python -c "
from app.gui.dashboard_main import DashboardMainWindow
from app.interfaces.desktop.integration import initialize_desktop_adapter

adapter = initialize_desktop_adapter('test')
window = DashboardMainWindow()
window.set_desktop_adapter(adapter)

# This should route through governance now
window.approve_selected()  # Should call adapter.execute()
"
```

---

## 🚀 Execution Order

1. **Fix dashboard_main.py** (8 handlers) - 2 hours
   - Primary dashboard, most critical paths

2. **Fix dashboard.py** (11 handlers) - 2 hours
   - Leather Book UI, user-facing actions

3. **Fix panel handlers** (10-15 handlers) - 3 hours
   - god_tier_panel, cerberus_panel, hydra_50_panel, etc.

4. **Test integration** - 1 hour
   - Smoke test all modified handlers
   - Verify governance pipeline receives actions
   - Check audit logs show desktop traffic

5. **Update truth map** - 30 minutes
   - Re-run grep scans
   - Document actual convergence rate

**Total Time**: 8 hours for complete desktop convergence

---

## 💡 Key Insight

**The problem wasn't**:
- Missing infrastructure ✅ (exists)
- Missing adapter ✅ (exists)  
- Missing routing method ✅ (exists)

**The problem was**:
- Handler methods never call `_route_through_governance()` ❌
- They call core systems directly instead ❌

**The fix**:
- Not 345 patches
- Just wire 30-35 convergence points to existing infrastructure
- Each convergence point routes 5-20 dependent methods

**This is convergence, not construction.**

---

## 🎯 Next Action

Start with `dashboard_main.py` - wire the 8 critical handlers:
1. `approve_selected()` 
2. `deny_selected()`
3. `run_codex_fix()`
4. `activate_selected()`
5. `run_qa_on_selected()`
6. `grant_integrator()`
7. `export_audit()`
8. `toggle_agents()`

These 8 methods route ~50 GUI operations through governance.

**No more analysis. Start wiring.**
