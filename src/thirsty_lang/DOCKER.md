# Docker Guide for Thirsty-lang 🐳💧

This guide explains how to use Docker with Thirsty-lang for containerized development and deployment.

## Quick Start

### Using Docker Compose (Recommended)

```bash
# Build and start all services
docker-compose up

# Start specific service
docker-compose up thirsty-dev

# Run in detached mode
docker-compose up -d
```

### Using Docker Directly

```bash
# Build the image
docker build -t thirsty-lang .

# Run a Thirsty-lang program
docker run --rm -v $(pwd)/examples:/app/examples thirsty-lang node src/cli.js examples/hello.thirsty

# Run the REPL
docker run -it --rm thirsty-lang npm run repl
```

## Available Services

### 1. thirsty (Production)

Main production service for running Thirsty-lang programs.

```bash
docker-compose up thirsty
```

**Use cases:**

- Running Thirsty-lang programs
- Production deployment
- CLI tool usage

### 2. thirsty-dev (Development)

Development environment with all tools installed.

```bash
docker-compose up thirsty-dev
```

**Features:**

- All development dependencies
- Hot-reloading with volume mounts
- Node.js debugging support (port 9229)
- Interactive terminal

### 3. repl (Node.js REPL)

Interactive Node.js REPL for Thirsty-lang.

```bash
docker-compose run --rm repl
```

**Use cases:**

- Interactive coding
- Testing code snippets
- Learning Thirsty-lang

### 4. python-repl (Python REPL)

Interactive Python REPL for Thirsty-lang.

```bash
docker-compose run --rm python-repl
```

**Use cases:**

- Using Python implementation
- Testing Python interpreter
- Alternative REPL experience

### 5. training

Interactive training program.

```bash
docker-compose run --rm training
```

**Use cases:**

- Learning Thirsty-lang
- Interactive tutorials
- Skill progression

### 6. playground

Web-based playground accessible via browser.

```bash
docker-compose up playground
```

Access at: http://localhost:8888

**Use cases:**

- Browser-based coding
- Quick experimentation
- Demos and presentations

## Common Tasks

### Run a Thirsty-lang Program

```bash
# Using Docker Compose
docker-compose run --rm thirsty node src/cli.js examples/hello.thirsty

# Using Docker directly
docker run --rm -v $(pwd)/examples:/app/examples thirsty-lang node src/cli.js examples/hello.thirsty
```

### Start Interactive REPL

```bash
# Node.js REPL
docker-compose run --rm repl

# Python REPL
docker-compose run --rm python-repl
```

### Run Tests

```bash
docker-compose run --rm thirsty npm test
```

### Format Code

```bash
docker-compose run --rm thirsty npm run format examples/hello.thirsty
```

### Lint Code

```bash
docker-compose run --rm thirsty npm run lint examples/hello.thirsty
```

### Profile Performance

```bash
docker-compose run --rm thirsty npm run profile examples/hello.thirsty
```

### Generate Documentation

```bash
docker-compose run --rm thirsty npm run doc examples/hello.thirsty
```

### Transpile Code

```bash
docker-compose run --rm thirsty node src/transpiler.js examples/hello.thirsty --target python
```

## Development Workflow

### 1. Start Development Environment

```bash
docker-compose up -d thirsty-dev
```

### 2. Attach to Container

```bash
docker-compose exec thirsty-dev bash
```

### 3. Make Changes

Your local files are mounted, so changes are reflected immediately.

### 4. Test Changes

```bash
docker-compose exec thirsty-dev npm test
```

### 5. Stop Services

```bash
docker-compose down
```

## Volume Management

### Named Volumes

- `node_modules` - Node.js dependencies
- `thirsty-data` - Persistent data
- `thirsty-venv` - Python virtual environment

### Bind Mounts

```yaml
volumes:
  - ./examples:/app/examples  # Example programs
  - ./src:/app/src            # Source code
```

## Port Mapping

| Service | Container Port | Host Port | Purpose |
|---------|---------------|-----------|---------|
| thirsty | 8080 | 8080 | Main service |
| thirsty-dev | 9229 | 9229 | Node.js debugger |
| playground | 8080 | 8888 | Web playground |

## Environment Variables

### Production (thirsty)

```bash
NODE_ENV=production
THIRSTY_VERSION=1.0.0
```

### Development (thirsty-dev)

```bash
NODE_ENV=development
THIRSTY_DEBUG=true
```

## Building Images

### Build All Services

```bash
docker-compose build
```

### Build Specific Service

```bash
docker-compose build thirsty-dev
```

### Build with No Cache

```bash
docker-compose build --no-cache
```

## Cleaning Up

### Stop All Services

```bash
docker-compose down
```

### Remove Volumes

```bash
docker-compose down -v
```

### Remove Images

```bash
docker-compose down --rmi all
```

### Complete Cleanup

```bash
docker-compose down -v --rmi all --remove-orphans
```

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker-compose logs thirsty

# Check specific service logs
docker-compose logs thirsty-dev
```

### Permission Issues

```bash
# Rebuild with proper permissions
docker-compose build --no-cache
```

### Port Already in Use

Change ports in `docker-compose.yml`:
```yaml
ports:
  - "8081:8080"  # Change host port
```

### Volume Issues

```bash
# Remove volumes and rebuild
docker-compose down -v
docker-compose up --build
```

## Advanced Usage

### Custom Dockerfile Build

```bash
# Build only base stage
docker build --target node-base -t thirsty-lang:base .

# Build development stage
docker build --target development -t thirsty-lang:dev .
```

### Running with Custom Network

```bash
docker network create thirsty-net
docker run --network thirsty-net thirsty-lang
```

### Multi-Stage Build Benefits

1. **Smaller production images** - Only production dependencies
1. **Separate dev environment** - Full tooling for development
1. **Build optimization** - Layer caching
1. **Security** - Minimal attack surface in production

## Production Deployment

### Using Docker

```bash
# Build production image
docker build -t thirsty-lang:1.0.0 .

# Run in production
docker run -d \
  --name thirsty-prod \
  --restart unless-stopped \
  -v /path/to/programs:/app/programs \
  thirsty-lang:1.0.0
```

### Using Docker Compose

```bash
# Production compose file
docker-compose -f docker-compose.yml up -d thirsty
```

## Best Practices

1. **Use .dockerignore** - Exclude unnecessary files
1. **Layer caching** - Order Dockerfile commands efficiently
1. **Multi-stage builds** - Separate dev and prod
1. **Named volumes** - Persist important data
1. **Health checks** - Monitor container health
1. **Resource limits** - Set memory and CPU limits
1. **Logging** - Configure proper logging drivers
1. **Security** - Run as non-root user (already configured)

## Security Considerations

- ✅ Non-root user (thirsty:1001)
- ✅ Minimal base image (Alpine)
- ✅ No unnecessary packages
- ✅ Read-only root filesystem (can be enabled)
- ✅ No secrets in image

## Integration with CI/CD

```yaml
# Example GitHub Actions workflow
- name: Build Docker image
  run: docker build -t thirsty-lang .

- name: Run tests in Docker
  run: docker run thirsty-lang npm test

- name: Push to registry
  run: docker push thirsty-lang:latest
```

## Support

For issues with Docker setup:

1. Check logs: `docker-compose logs`
1. Verify Docker version: `docker --version`
1. Check compose version: `docker-compose --version`
1. Review this guide
1. Open an issue on GitHub

## Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Best Practices Guide](https://docs.docker.com/develop/dev-best-practices/)

---

Stay hydrated and containerize responsibly! 🐳💧✨
