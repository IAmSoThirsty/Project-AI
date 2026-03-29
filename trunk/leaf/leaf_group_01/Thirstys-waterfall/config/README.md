<!-- # ============================================================================ # -->
<!-- # STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59 # -->
<!-- # COMPLIANCE: Sovereign Substrate / README.md # -->
<!-- # ============================================================================ # -->
<div align="right">
  <img src="https://img.shields.io/badge/DATE-2026-03-18-blueviolet?style=for-the-badge" alt="Date" />
  <img src="https://img.shields.io/badge/PRODUCTIVITY-ACTIVE-success?style=for-the-badge" alt="Productivity" />
</div>
<!-- # ============================================================================ #


<!-- # COMPLIANCE: Sovereign Substrate / README.md # -->
<!-- # ============================================================================ #

<!-- # Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master -->
# Configuration Directory

This directory contains production configuration templates for Thirstys Waterfall.

## Files

- `production.json` - Production environment configuration template

## Usage

### For Production Deployment

Copy the production template and customize for your environment:

```bash
cp production.json my-production.json
```

Edit `my-production.json` with your specific settings, then start the system:

```bash
thirstys-waterfall --config config/my-production.json --start
```

### Environment Variables

Configuration can also be set via environment variables. See `.env.example` in the repository root.

## Configuration Options

See the main [README.md](../README.md) for detailed configuration options.
