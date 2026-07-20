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
