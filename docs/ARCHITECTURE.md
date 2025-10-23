# Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Load Balancer (Nginx)                    │
└───────────────────────────┬─────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│                       FastAPI Application                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  API Routes  │  │ Controllers  │  │   Services   │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                  │                  │                  │
│         └──────────────────┴──────────────────┘                  │
└───────────────────────────┬─────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
┌───────▼────────┐  ┌──────▼──────┐   ┌───────▼────────┐
│   LiteLLM      │  │    Redis    │   │     NATS       │
│   Proxy        │  │    Cache    │   │  Message Queue │
└───────┬────────┘  └─────────────┘   └────────────────┘
        │
┌───────▼────────┐
│  Gemini LLM    │
│   (Google AI)  │
└────────────────┘

Observability Stack:
┌────────────┐  ┌────────────┐  ┌────────────┐
│ Langfuse   │  │ Prometheus │  │  Grafana   │
└────────────┘  └────────────┘  └────────────┘
```

---

## Component Details

### 1. FastAPI Application (Port 6000 external, 8000 internal)

**Responsibilities:**
- Handle HTTP requests
- Request validation
- Authentication & authorization
- Rate limiting
- Response formatting

**Key Layers:**

#### API Layer (`app/api/`)
- Route definitions
- Request/response schemas
- Endpoint handlers

#### Core Layer (`app/core/`)
- Configuration management
- Logging setup
- Exception handling
- Middleware

#### Services Layer (`app/services/`)
- **LLMService**: Communicate with LiteLLM proxy
- **CodeExtractionService**: Parse code from LLM responses
- **CacheService**: Redis caching operations
- **ObservabilityService**: Langfuse integration

#### Models Layer (`app/models/`)
- Pydantic schemas
- Domain models
- Enumerations

#### Helpers Layer (`app/helpers/`)
- PromptBuilder: Construct LLM prompts
- Validators: Input validation
- RateLimiter: Request rate limiting

---

### 2. LiteLLM Proxy (Port 4000)

**Purpose:** Unified interface to multiple LLM providers

**Features:**
- Provider abstraction
- Automatic retries
- Fallback routing
- Request logging
- Cost tracking

**Configuration:** `infrastructure/litellm/config.yaml`

**Supported Models:**
- Gemini Pro
- Gemini 1.5 Pro
- Gemini 1.5 Flash
- Extensible to other providers

---

### 3. Redis Cache (Port 6379)

**Purpose:** High-performance caching

**Use Cases:**
- Cache generated code results
- Session storage
- Rate limit counters
- Temporary data storage

**Configuration:**
- Maxmemory: 256MB (adjustable)
- Eviction policy: allkeys-lru
- Persistence: AOF + RDB

---

### 4. NATS Message Queue (Port 4222)

**Purpose:** Async job processing

**Use Cases:**
- Background code generation
- File processing tasks
- Cleanup jobs

**Features:**
- JetStream for persistence
- At-least-once delivery
- Consumer groups

---

### 5. Langfuse (Port 3000)

**Purpose:** LLM observability and tracing

**Tracked Metrics:**
- Prompt templates
- LLM responses
- Token usage
- Latency
- Success/failure rates

---

### 6. Prometheus (Port 9090)

**Purpose:** Metrics collection

**Metrics:**
- Request rates
- Response times
- Error rates
- Token usage
- Cache hit rates

---

### 7. Grafana (Port 3001)

**Purpose:** Metrics visualization

**Dashboards:**
- System overview
- API performance
- LLM usage
- Error tracking

---

## Request Flow

### Synchronous Code Generation

```
1. Client sends POST /api/v1/generate_code
   ↓
2. API validates request (schemas, rate limits)
   ↓
3. Check Redis cache for existing result
   ↓ (cache miss)
4. PromptBuilder constructs LLM prompt
   ↓
5. LLMService calls LiteLLM proxy
   ↓
6. LiteLLM routes to Gemini
   ↓
7. Gemini generates code
   ↓
8. CodeExtractionService parses response
   ↓
9. Result cached in Redis
   ↓
10. Response sent to client
```

### Asynchronous Code Generation

```
1. Client sends POST /api/v1/generate_code (async=true)
   ↓
2. API creates job and returns job_id
   ↓
3. Job published to NATS queue
   ↓
4. Worker picks up job
   ↓
5. Worker generates code (steps 4-8 above)
   ↓
6. Result stored in Redis with job_id
   ↓
7. Client polls GET /api/v1/jobs/{job_id}
```

---

## Data Flow

### Code Generation Pipeline

```
User Prompt
    ↓
[Validation]
    ↓
[Framework Detection]
    ↓
[Prompt Building]
    ↓
[LLM Generation]
    ↓
[Code Extraction]
    ↓
[File Organization]
    ↓
[Response Formatting]
    ↓
Generated Files
```

---

## Security Architecture

### Layers of Security

1. **Network Layer**
   - Nginx reverse proxy
   - Rate limiting
   - IP filtering (optional)

2. **Application Layer**
   - API key authentication
   - Request validation
   - Input sanitization
   - CORS configuration

3. **Data Layer**
   - Redis password protection
   - Environment variable encryption
   - No sensitive data in logs

4. **Monitoring Layer**
   - Audit logs
   - Anomaly detection
   - Alert notifications

---

## Scalability

### Horizontal Scaling

**Application Tier:**
- Stateless FastAPI instances
- Load balanced via Nginx
- Session affinity not required (stateless)

**Cache Tier:**
- Redis Cluster for high availability
- Read replicas for scaling reads

**Queue Tier:**
- NATS clustering
- Multiple consumers for workers

### Vertical Scaling

- Increase container resources (CPU, memory)
- Adjust worker count per application instance
- Optimize LLM batch processing

---

## Error Handling

### Exception Hierarchy

```
Exception
└── AppException
    ├── LLMServiceException
    ├── CodeExtractionException
    ├── CacheException
    ├── RateLimitException
    └── ValidationException
```

### Error Recovery

1. **LLM Failures**: Retry with exponential backoff
2. **Cache Failures**: Degrade gracefully, continue without cache
3. **Queue Failures**: Dead letter queue for manual review
4. **Validation Errors**: Return detailed error messages

---

## Monitoring Strategy

### Health Checks

- `/health` endpoint for load balancer
- Component-level health checks
- Dependency health validation

### Metrics Collection

- Request/response metrics (Prometheus)
- LLM usage metrics (Langfuse)
- System metrics (Docker stats)
- Custom business metrics

### Logging

- Structured JSON logging
- Log levels: DEBUG, INFO, WARNING, ERROR
- Correlation IDs for request tracing
- Centralized log aggregation (optional)

---

## Future Enhancements

1. **Authentication**
   - OAuth2 integration
   - User management
   - API key management

2. **Code Quality**
   - Linting generated code
   - Security scanning
   - Dependency vulnerability checks

3. **Figma Integration**
   - Design-to-code generation
   - Component extraction from Figma

4. **GitHub Integration**
   - Direct repository commits
   - Pull request creation
   - CI/CD integration

5. **Multi-tenancy**
   - Organization management
   - Resource quotas
   - Billing integration

