# Stage 6 Legacy Source Map

The Stage 6 governance package is a clean kernel-dependent implementation. It
preserves the current canonical outcomes and unilateral veto while avoiding
the legacy package's upward and application-level dependencies.

| Legacy file | SHA-256 |
|---|---|
| `src/app/core/governance.py` | `A82750B987D8A69E21E01AEA5F4DAA43EF517A492BFB7C8B72C0C467E95F44B6` |
| `src/app/core/governance_kernel.py` | `84760A6AD50531FADACE2B5FE75047AF8DC1DE2605C8C9C8E23E2194EE76F870` |
| `src/app/core/governance_outcomes.py` | `83132B4518D9C72D49EB27E551F3C09D9BE4A044DD4329009E5CC86BE7807F30` |
| `src/app/core/governance_quorum.py` | `0A27DA121BB78DC7F8B08DF77FD5F57F2DCD134C203F97FED194307D21BEEBD7` |
| `src/app/core/governance_observability.py` | `3FE83E78F4D74177988B99AE5E9254091BB5871B30FFA077D46BF22FD4523C59` |
| `src/app/core/governance_drift_monitor.py` | `A2A6ED497498BE2B0536D368AE7C9B96FEBB79DF704EC8C3ECD621E4596BA736` |
| `src/app/core/governance_graph.py` | `1D5994367B8AF57A04BA5A44CD5D8D9B19E774C38C6F74E52EEF080093B9026E` |

All legacy reads were guarded by the Stage 3 soft-freeze boundary.
