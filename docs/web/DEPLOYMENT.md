# Deployment Guide for Project-AI Web

## Docker Deployment

### Option 1: Docker Compose (Recommended)

Create `docker-compose.yml` in the web directory:

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=postgresql://username:REPLACE_WITH_SECURE_PASSWORD@db:5432/projectai
    depends_on:
      - db

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend

  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=projectai
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

Run with:
```bash
docker-compose up -d
```

## Cloud Deployment Options

### Vercel (Frontend)
1. Connect your GitHub repo to Vercel
2. Set root directory to `web/frontend`
3. Deploy automatically on push

### Heroku (Full Stack)
```bash
heroku create project-ai-web
heroku addons:create heroku-postgresql:hobby-dev
git push heroku feature/web-conversion:main
```

### AWS (Production)
- **Frontend**: S3 + CloudFront
- **Backend**: EC2 or ECS
- **Database**: RDS PostgreSQL

### DigitalOcean App Platform
1. Connect GitHub repository
2. Configure build settings
3. Deploy with auto-scaling

## Environment Variables for Production

```env
# Backend
FLASK_ENV=production
SECRET_KEY=<generate-strong-secret>
JWT_SECRET_KEY=<generate-strong-jwt-secret>
DATABASE_URL=<production-database-url>
CORS_ORIGINS=https://yourdomain.com

# API Keys
OPENAI_API_KEY=<your-key>
GEMINI_API_KEY=<your-key>
```

## Security Checklist

- [ ] Change all default secret keys
- [ ] Enable HTTPS/SSL
- [ ] Configure CORS properly
- [ ] Set up rate limiting
- [ ] Enable authentication on all endpoints
- [ ] Use environment variables for sensitive data
- [ ] Set up database backups
- [ ] Configure logging and monitoring


---

**Repository note:** Last updated: 2025-11-26 (automated)

<!-- last-updated-marker -->
