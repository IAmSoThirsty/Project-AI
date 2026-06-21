# Stage 14.5 Desktop Source Map

| Source | SHA-256 | Disposition |
|---|---|---|
| `T:\Project-AI-main\desktop\src\App.tsx` | `67b67ffac4673e67341acce1788ebb8c234f33bd176daafeabe8246053ecb0d2` | Sidebar/page structure reference |
| `T:\Project-AI-main\desktop\src\pages\Dashboard.tsx` | `0cd61288e07c5d3d83ba86815770b8ea1429577bd65794a8308837ad8aa25f90` | Status-card reference; legacy doctrine claims rejected |
| `T:\Project-AI-main\desktop\src\pages\Audit.tsx` | `767673045ec31d87b7a20ed575659178dda8a419c6b1381d57f8ed60bc41871b` | Audit-table reference |
| `T:\Project-AI-main\desktop\src\api\governance.ts` | `888cc16c27c5fffa4eab160dec1db0019cbac820ba02e3925ddc02d56c17373e` | API-client reference; direct intent submission rejected |
| `T:\Project-AI-main\src\app\interfaces\desktop\adapter.py` | `d81352e30421bf9bd81dd61a506b1a2e93d5e8be48e0e06891a8e3aaaba04315` | Governance-routing intent retained as API-only boundary; direct runtime imports rejected |

The new PyQt6 implementation does not copy the Electron/React skeleton. Voice,
chat, image generation, persona mutation, and editor surfaces remain deferred.
