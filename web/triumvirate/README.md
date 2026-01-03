# The_Triumvirate Placeholder

This directory is reserved for The_Triumvirate web frontend repository.

## Status

⚠️ **The_Triumvirate repository is not yet integrated**

This placeholder will be replaced when The_Triumvirate repository becomes available.

## Integration Instructions

### When The_Triumvirate Repository is Available

1. **Remove this placeholder:**
   ```bash
   rm -rf web/triumvirate
   ```

2. **Add as git submodule:**
   ```bash
   git submodule add https://github.com/IAmSoThirsty/The_Triumvirate.git web/triumvirate
   ```

3. **Initialize and update:**
   ```bash
   git submodule update --init --recursive
   ```

4. **Install dependencies:**
   ```bash
   cd web/triumvirate
   npm install
   ```

5. **Configure environment:**
   ```bash
   # Update .env in project root
   ENABLE_TRIUMVIRATE=true
   ```

6. **Start development:**
   ```bash
   npm run triumvirate:dev
   ```

### Alternative: Use Integration Script

```bash
# Run from project root
./scripts/integrate_triumvirate.sh
```

## Documentation

For detailed integration instructions, see:
- `TRIUMVIRATE_INTEGRATION.md` - Complete integration guide
- `web/README.md` - Quick start guide
- `scripts/integrate_triumvirate.sh` - Automated integration script

## Repository Information

- **Expected Repository**: https://github.com/IAmSoThirsty/The_Triumvirate.git
- **Integration Method**: Git Submodule
- **Branch**: main
- **Purpose**: Modern web frontend for Project-AI

## Current Web Structure

While The_Triumvirate is not yet available, the legacy web frontend is located at:
- Backend: `web/backend/app.py`
- Frontend: `web/frontend/index.html`

## Questions?

If The_Triumvirate repository exists but you're seeing this placeholder:
1. Verify the repository URL
2. Check access permissions
3. Run the integration script: `./scripts/integrate_triumvirate.sh`
4. See `TRIUMVIRATE_INTEGRATION.md` for troubleshooting

---

**Last Updated**: 2026-01-03
**Status**: Awaiting Repository Availability
