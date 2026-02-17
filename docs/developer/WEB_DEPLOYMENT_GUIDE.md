# WEB DEPLOYMENT GUIDE - Project AI Governance

## 🌐 **Deploy Web Frontend to Your Domain**

______________________________________________________________________

## **Option 1: Static Hosting (Recommended for Web Frontend)**

### **A. Deploy to Netlify (Easiest)**

1. **Prepare the web directory:**

```bash
cd web

# Your files: index.html, styles.css, app.js

```

2. **Install Netlify CLI:**

```bash
npm install -g netlify-cli
```

3. **Deploy:**

```bash
netlify login
netlify deploy --prod --dir=../web
```

4. **Configure custom domain:**

- Go to Netlify dashboard → Domain settings
- Add your custom domain (e.g., `governance.yourdomain.com`)
- Update DNS records as instructed

### **B. Deploy to Vercel**

1. **Install Vercel CLI:**

```bash
npm install -g vercel
```

2. **Deploy:**

```bash
cd web
vercel --prod
```

3. **Add custom domain:**

```bash
vercel domains add governance.yourdomain.com
```

### **C. Deploy to GitHub Pages**

1. **Create `web/.nojekyll` file:**

```bash
cd web
touch .nojekyll
```

2. **Push to GitHub:**

```bash
git add .
git commit -m "Deploy web to GitHub Pages"
git push origin main
```

3. **Enable GitHub Pages:**

- Go to repository settings → Pages
- Source: `main` branch, `/web` folder
- Custom domain: `governance.yourdomain.com`

4. **Configure DNS:**

Add CNAME record: `governance` → `your-username.github.io`

______________________________________________________________________

## **Option 2: Full Stack Deployment (API + Web)**

### **A. Deploy to Your VPS/Cloud Server**

**Prerequisites:**

- Ubuntu/Debian server
- Domain name with DNS access
- SSH access

**1. Install Dependencies:**

```bash

# SSH into your server

ssh user@your-server.com

# Update system

sudo apt update && sudo apt upgrade -y

# Install Python, Nginx, Certbot

sudo apt install python3 python3-pip nginx certbot python3-certbot-nginx -y
```

**2. Clone Repository:**

```bash
cd /var/www
sudo git clone https://github.com/yourusername/Project-AI.git
cd Project-AI
sudo chown -R $USER:$USER .
```

**3. Setup Backend API:**

```bash

# Install Python dependencies

pip3 install -r requirements.txt

# Create systemd service

sudo nano /etc/systemd/system/project-ai-api.service
```

Add:

```ini
[Unit]
Description=Project AI Governance API
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/Project-AI
Environment="PATH=/usr/bin"
ExecStart=/usr/bin/python3 start_api.py
Restart=always

[Install]
WantedBy=multi-user.target
```

**4. Start API Service:**

```bash
sudo systemctl daemon-reload
sudo systemctl enable project-ai-api
sudo systemctl start project-ai-api
sudo systemctl status project-ai-api
```

**5. Configure Nginx:**

```bash
sudo nano /etc/nginx/sites-available/governance.yourdomain.com
```

Add:

```nginx
server {
    server_name governance.yourdomain.com;

    # Web Frontend

    location / {
        root /var/www/Project-AI/web;
        index index.html;
        try_files $uri $uri/ =404;
    }

    # API Backend

    location /api {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**6. Enable Site:**

```bash
sudo ln -s /etc/nginx/sites-available/governance.yourdomain.com /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

**7. Setup SSL (HTTPS):**

```bash
sudo certbot --nginx -d governance.yourdomain.com
sudo systemctl restart nginx
```

**8. Configure DNS:** Add A record: `governance` → `your-server-ip`

______________________________________________________________________

### **B. Deploy to AWS (S3 + CloudFront)**

**For Static Web Only:**

1. **Create S3 Bucket:**

```bash
aws s3 mb s3://governance.yourdomain.com
```

2. **Upload Web Files:**

```bash
cd web
aws s3 sync . s3://governance.yourdomain.com --acl public-read
```

3. **Enable Static Website Hosting:**

```bash
aws s3 website s3://governance.yourdomain.com --index-document index.html
```

4. **Setup CloudFront Distribution:**

- Create distribution pointing to S3 bucket
- Add alternate domain name: `governance.yourdomain.com`
- Request SSL certificate via ACM

5. **Update DNS:**

- Add CNAME: `governance` → `d111111abcdef8.cloudfront.net`

______________________________________________________________________

### **C. Deploy to Heroku (Full Stack)**

1. **Create Heroku App:**

```bash
heroku login
heroku create project-ai-governance
```

2. **Create `Procfile`:**

```bash
echo "web: python start_api.py" > Procfile
```

3. **Deploy:**

```bash
git add .
git commit -m "Deploy to Heroku"
git push heroku main
```

4. **Add Custom Domain:**

```bash
heroku domains:add governance.yourdomain.com
```

5. **Configure DNS:**

Add CNAME: `governance` → `your-app-name.herokuapp.com`

______________________________________________________________________

### **D. Deploy with Docker (Any Platform)**

1. **Build Docker Image:**

```bash
docker-compose build
```

2. **Run Containers:**

```bash
docker-compose up -d
```

3. **Configure Reverse Proxy (Nginx):**

```nginx
location / {
    proxy_pass http://localhost:8000;  # Web
}
location /api {
    proxy_pass http://localhost:8001;  # API
}
```

______________________________________________________________________

## **DNS Configuration Summary**

**For any deployment, update your DNS:**

| Record Type | Name       | Value            | TTL  |
| ----------- | ---------- | ---------------- | ---- |
| A           | governance | `your-server-ip` | 3600 |

**OR for CDN/Cloud:**

| Record Type | Name       | Value          | TTL  |
| ----------- | ---------- | -------------- | ---- |
| CNAME       | governance | `your-cdn-url` | 3600 |

______________________________________________________________________

## **Quick Deployment Commands**

### **Netlify (Fastest):**

```bash
cd web
netlify deploy --prod
```

### **Your Server (Full Control):**

```bash

# On server

cd /var/www/Project-AI
sudo systemctl restart project-ai-api
sudo systemctl restart nginx
```

### **Docker (Portable):**

```bash
docker-compose up -d
```

______________________________________________________________________

## **Post-Deployment Checklist**

- [ ] SSL certificate installed (HTTPS)
- [ ] API accessible at `https://governance.yourdomain.com/api/health`
- [ ] Web frontend loads at `https://governance.yourdomain.com`
- [ ] CORS configured for your domain in `config/settings.py`
- [ ] Environment variables set (`.env` configured)
- [ ] Monitoring enabled (Prometheus/Grafana)
- [ ] Backups configured for audit logs
- [ ] Firewall rules configured

______________________________________________________________________

## **Update `.env` for Production**

```bash

# API Configuration

API_HOST=0.0.0.0
API_PORT=8001
API_DEBUG=False

# CORS

ENABLE_CORS=True
ALLOWED_ORIGINS=https://governance.yourdomain.com

# Logging

LOG_LEVEL=INFO
LOG_FILE=/var/log/project-ai/api.log
```

______________________________________________________________________

## **Monitoring Your Deployment**

Access monitoring at:

- **Grafana:** `https://governance.yourdomain.com:3000`
- **Prometheus:** `https://governance.yourdomain.com:9090`
- **API Health:** `https://governance.yourdomain.com/api/health`

______________________________________________________________________

**Your web frontend will be live at: `https://governance.yourdomain.com`** 🚀
