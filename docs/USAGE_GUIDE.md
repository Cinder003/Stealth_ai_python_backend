# Usage Guide

Complete guide to using the Unified Code Generation Platform.

---

## Getting Started

### 1. Start the Platform

```bash
cd stealth_ai
make setup
make prod
```

Wait for all services to start (approximately 30-60 seconds).

### 2. Verify Services

```bash
curl http://localhost:6000/health
```

---

## Basic Usage

### Generate a React Component

```bash
curl -X POST http://localhost:6000/api/v1/generate_code \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Create a button component with loading state",
    "code_type": "component",
    "framework": "react",
    "styling": "tailwindcss"
  }'
```

**Response:**

```json
{
  "success": true,
  "files": [
    {
      "path": "src/components/Button.jsx",
      "content": "import React from 'react';\n\nconst Button = ({ children, loading, onClick }) => { ... }",
      "language": "jsx",
      "size_bytes": 850
    }
  ],
  "total_files": 1,
  "total_lines": 32,
  "generation_time_seconds": 2.1
}
```

---

## Advanced Examples

### 1. Production-Ready React App

```bash
curl -X POST http://localhost:6000/api/v1/generate_code \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Create a dashboard with user profile, statistics cards, and recent activity feed. Include dark mode toggle.",
    "code_type": "frontend",
    "framework": "react",
    "production_ready": true,
    "include_tests": true,
    "styling": "tailwindcss",
    "additional_context": {
      "theme": "modern",
      "color_scheme": "blue and purple"
    }
  }'
```

**Features included:**
- ✅ Error boundaries
- ✅ Loading states
- ✅ TypeScript types/PropTypes
- ✅ Accessibility attributes
- ✅ Responsive design
- ✅ Jest tests
- ✅ README with setup instructions

---

### 2. Node.js REST API

```bash
curl -X POST http://localhost:6000/api/v1/generate_code \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Create a REST API for a task management system with users, projects, and tasks. Include authentication with JWT.",
    "code_type": "backend",
    "framework": "express",
    "production_ready": true,
    "include_tests": true
  }'
```

**Features included:**
- ✅ Express.js server
- ✅ JWT authentication
- ✅ Input validation
- ✅ Error handling middleware
- ✅ Rate limiting
- ✅ API documentation
- ✅ Integration tests
- ✅ Environment configuration

---

### 3. Fullstack Application

```bash
curl -X POST http://localhost:6000/api/v1/generate_code \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Create a blog platform where users can create, edit, and publish posts. Include user authentication, comments, and tags.",
    "code_type": "fullstack",
    "production_ready": true,
    "include_tests": true,
    "additional_context": {
      "database": "PostgreSQL",
      "deployment": "Docker"
    }
  }'
```

**Includes:**
- Frontend (React)
- Backend (Node.js/Express)
- Database schema
- Docker configuration
- API documentation
- Tests for both frontend and backend

---

## Framework Options

### Frontend Frameworks

#### React (Default)
```json
{
  "framework": "react",
  "styling": "tailwindcss"
}
```

#### React with TypeScript
```json
{
  "framework": "react-typescript",
  "styling": "styled-components"
}
```

#### Next.js
```json
{
  "framework": "nextjs",
  "styling": "tailwindcss"
}
```

#### Vue 3
```json
{
  "framework": "vue",
  "styling": "tailwindcss"
}
```

### Backend Frameworks

#### Node.js/Express (Default)
```json
{
  "framework": "express"
}
```

#### NestJS
```json
{
  "framework": "nestjs"
}
```

#### FastAPI (Python)
```json
{
  "framework": "fastapi"
}
```

---

## Styling Options

### Tailwind CSS (Recommended)
```json
{
  "styling": "tailwindcss"
}
```

### CSS Modules
```json
{
  "styling": "css-modules"
}
```

### Styled Components
```json
{
  "styling": "styled-components"
}
```

### Plain CSS
```json
{
  "styling": "css"
}
```

---

## LLM Model Selection

### Fast Generation (Default)
```json
{
  "model": "gemini/gemini-1.5-flash-latest"
}
```
- Fastest response
- Good for simple components
- Lower cost

### High Quality
```json
{
  "model": "gemini/gemini-1.5-pro-latest"
}
```
- Best code quality
- Complex applications
- Higher cost

---

## Tips for Better Results

### 1. Be Specific

❌ Bad:
```json
{
  "prompt": "Create a form"
}
```

✅ Good:
```json
{
  "prompt": "Create a contact form with name, email, phone, and message fields. Include validation, error messages, and a success notification."
}
```

### 2. Provide Context

```json
{
  "prompt": "Create a product card component",
  "additional_context": {
    "fields": ["image", "title", "price", "rating", "add to cart button"],
    "style": "modern e-commerce",
    "interactions": ["hover effects", "favorite button"]
  }
}
```

### 3. Use Production Mode for Complete Apps

```json
{
  "production_ready": true,
  "include_tests": true,
  "include_documentation": true
}
```

### 4. Specify Technical Details

```json
{
  "prompt": "Create a data table with sorting, filtering, and pagination",
  "additional_context": {
    "data_source": "REST API",
    "pagination": "server-side",
    "features": ["search", "column sorting", "row selection"]
  }
}
```

---

## Working with Generated Code

### Save to Files

```bash
# Using jq to extract files
curl -X POST http://localhost:6000/api/v1/generate_code \
  -H "Content-Type: application/json" \
  -d '{"prompt": "...", "code_type": "frontend"}' \
  | jq -r '.files[] | @text "\(.path)\n\(.content)"' > output.txt
```

### Python Script Example

```python
import requests
import os

response = requests.post(
    'http://localhost:6000/api/v1/generate_code',
    json={
        'prompt': 'Create a login form with email and password',
        'code_type': 'component',
        'framework': 'react'
    }
)

result = response.json()

# Create files
for file in result['files']:
    path = file['path']
    content = file['content']
    
    # Create directory if needed
    os.makedirs(os.path.dirname(path), exist_ok=True)
    
    # Write file
    with open(path, 'w') as f:
        f.write(content)
    
    print(f'Created: {path}')
```

---

## Monitoring Usage

### Check Metrics

```bash
curl http://localhost:6000/api/v1/metrics
```

### View Dashboards

- **Grafana**: http://localhost:3001 (admin/admin)
- **Prometheus**: http://localhost:9090
- **Langfuse**: http://localhost:3000

---

## Common Use Cases

### 1. Landing Page

```json
{
  "prompt": "Create a modern landing page for a SaaS product with hero section, features, pricing, and contact form",
  "code_type": "frontend",
  "framework": "nextjs",
  "production_ready": true,
  "styling": "tailwindcss"
}
```

### 2. Admin Dashboard

```json
{
  "prompt": "Create an admin dashboard with sidebar navigation, user management table, analytics charts, and settings page",
  "code_type": "frontend",
  "framework": "react-typescript",
  "production_ready": true,
  "styling": "tailwindcss"
}
```

### 3. E-commerce Product Page

```json
{
  "prompt": "Create a product page with image gallery, product details, reviews, and add to cart functionality",
  "code_type": "component",
  "framework": "react",
  "styling": "tailwindcss"
}
```

### 4. Authentication System

```json
{
  "prompt": "Create a complete authentication system with login, signup, password reset, and email verification",
  "code_type": "fullstack",
  "production_ready": true,
  "include_tests": true
}
```

### 5. CRUD API

```json
{
  "prompt": "Create a REST API for managing inventory items with CRUD operations, search, and pagination",
  "code_type": "backend",
  "framework": "express",
  "production_ready": true
}
```

---

## Troubleshooting

### Slow Generation

- Try using `gemini-1.5-flash` model
- Reduce scope of request
- Check LLM service health

### Empty or Incomplete Results

- Be more specific in prompt
- Add more context
- Use production_ready mode
- Try different model

### Rate Limit Errors

- Wait before retrying
- Increase limits in `.env.production`
- Use caching for repeated requests

---

## Best Practices

1. **Start Simple**: Begin with components, then build up to full apps
2. **Iterate**: Generate base code, then refine with additional requests
3. **Review Code**: Always review generated code before production use
4. **Test**: Run tests and add custom tests as needed
5. **Customize**: Use generated code as starting point, customize as needed
6. **Cache**: Similar requests are cached for faster responses

---

## Next Steps

- Explore API documentation: http://localhost:6000/docs
- Check monitoring dashboards
- Read architecture documentation
- Try different frameworks and styles

