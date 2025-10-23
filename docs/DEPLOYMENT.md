# Deployment Guide

## Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- At least 4GB RAM
- Gemini API Key

---

## Quick Start

### 1. Clone Repository

```bash
git clone <repository-url>
cd stealth_ai
```

### 2. Setup Environment

```bash
make setup
```

This creates necessary directories and copies environment templates.

### 3. Configure Environment

Edit `.env.production` and add your Gemini API key:

```bash
GEMINI_API_KEY=your-gemini-api-key-here
```

### 4. Start Services

```bash
make prod
```

This will:
- Build Docker images
- Start all services (App, Redis, NATS, LiteLLM, Langfuse, Prometheus, Grafana)
- Run database migrations
- Initialize storage

### 5. Verify Deployment

Check health:
```bash
curl http://localhost:6000/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "services": {
    "llm": "healthy",
    "cache": "healthy"
  }
}
```

---

## Service URLs

| Service | URL | Description |
|---------|-----|-------------|
| API | http://localhost:6000 | Main API endpoint |
| API Docs | http://localhost:6000/docs | Swagger UI |
| Health Check | http://localhost:6000/health | Health endpoint |
| Prometheus | http://localhost:9090 | Metrics collection |
| Grafana | http://localhost:3001 | Dashboards (admin/admin) |
| Langfuse | http://localhost:3000 | LLM observability |
| NATS Monitor | http://localhost:8222 | Queue monitoring |

---

## Environment Variables

### Required

```bash
GEMINI_API_KEY=your-gemini-api-key
SECRET_KEY=your-secret-key
```

### Optional

```bash
# Redis
REDIS_PASSWORD=your-redis-password

# Langfuse (if enabled)
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_ENABLED=true

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

---

## Production Checklist

### Security

- [ ] Change `SECRET_KEY` to a strong random value
- [ ] Set `REDIS_PASSWORD` to a strong password
- [ ] Enable HTTPS (configure Nginx with SSL certificates)
- [ ] Restrict CORS origins in `.env.production`
- [ ] Enable Langfuse for monitoring
- [ ] Set up firewall rules
- [ ] Use API key authentication

### Performance

- [ ] Adjust worker count based on CPU cores
- [ ] Configure Redis maxmemory
- [ ] Set up CDN for static assets (if any)
- [ ] Enable response compression
- [ ] Configure rate limiting appropriately

### Monitoring

- [ ] Configure Prometheus alerts
- [ ] Set up Grafana dashboards
- [ ] Enable application logging
- [ ] Configure log aggregation
- [ ] Set up uptime monitoring

### Backup

- [ ] Set up Redis persistence
- [ ] Back up environment variables
- [ ] Document configuration

---

## Scaling

### Horizontal Scaling

To scale the application horizontally:

```yaml
# docker-compose.yml
services:
  app:
    deploy:
      replicas: 3
```

Or use Docker Swarm / Kubernetes.

### Vertical Scaling

Increase container resources:

```yaml
services:
  app:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
```

---

## Troubleshooting

### LLM Service Connection Failed

```bash
# Check LiteLLM logs
docker logs codegen_litellm

# Verify Gemini API key
echo $GEMINI_API_KEY
```

### Redis Connection Issues

```bash
# Check Redis logs
docker logs codegen_redis

# Test Redis connection
docker exec -it codegen_redis redis-cli ping
```

### High Memory Usage

```bash
# Check container memory
docker stats

# Adjust Redis maxmemory
# Edit infrastructure/redis/redis.conf
maxmemory 512mb
```

### Slow Response Times

- Check Prometheus metrics at http://localhost:9090
- Review Grafana dashboards at http://localhost:3001
- Check LLM response times
- Verify cache hit rate

---

## Updating

### Update Application

```bash
git pull
docker-compose build app
docker-compose up -d app
```

### Update Dependencies

```bash
# Edit requirements.txt
docker-compose build app
docker-compose up -d app
```

---

## Backup & Restore

### Backup Redis Data

```bash
docker exec codegen_redis redis-cli SAVE
docker cp codegen_redis:/data/dump.rdb ./backup/
```

### Restore Redis Data

```bash
docker cp ./backup/dump.rdb codegen_redis:/data/
docker restart codegen_redis
```

---

## Monitoring Alerts

Configure alerts in `monitoring/alerts.yml`:

```yaml
groups:
  - name: codegen_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(code_generation_requests_total{status="error"}[5m]) > 0.1
        for: 5m
        annotations:
          summary: "High error rate detected"
```

---

## Support

For issues and questions:
- Check logs: `docker-compose logs`
- Review documentation in `/docs`
- Open an issue on GitHub

