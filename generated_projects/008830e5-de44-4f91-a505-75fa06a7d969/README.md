# Full-Stack Application with Docker

This is a full-stack application with a Node.js/Express backend and React frontend, both containerized with Docker.

## Project Structure

```
├── backend/           # Node.js/Express API with Prisma ORM
├── frontend/          # React application with Vite
└── docker-compose.yml # Orchestrates all services
```

## Prerequisites

- Docker and Docker Compose
- Git

## Quick Start

1. **Clone and navigate to the project:**
   ```bash
   git clone <repository-url>
   cd <project-directory>
   ```

2. **Set up environment variables:**
   ```bash
   # Copy the example environment file
   cp .env.example .env
   
   # Edit the .env file with your values
   # Make sure to set strong secrets for JWT tokens
   ```

3. **Start all services:**
   ```bash
   docker-compose up --build
   ```

4. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5000
   - Database: localhost:5432

## Environment Variables

### Required Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
# Database Configuration
POSTGRES_USER=myapp_user
POSTGRES_PASSWORD=myapp_password
POSTGRES_DB=myapp_database
DATABASE_URL=postgresql://myapp_user:myapp_password@postgres:5432/myapp_database

# JWT Secrets (use strong, random secrets)
ACCESS_TOKEN_SECRET=your_super_secret_access_token_key_here
REFRESH_TOKEN_SECRET=your_super_secret_refresh_token_key_here
```

## Services

### Backend (Port 5000)
- **Framework:** Node.js with Express
- **Database:** PostgreSQL with Prisma ORM
- **Authentication:** JWT-based
- **Features:** User authentication, dashboard API

### Frontend (Port 3000)
- **Framework:** React with TypeScript
- **Build Tool:** Vite
- **Styling:** Tailwind CSS
- **Features:** Login, Dashboard, Charts

### Database (Port 5432)
- **Type:** PostgreSQL 14
- **Persistent Storage:** Docker volume

## Development

### Running Individual Services

**Backend only:**
```bash
cd backend
docker build -t myapp-backend .
docker run -p 5000:5000 --env-file ../.env myapp-backend
```

**Frontend only:**
```bash
cd frontend
docker build -t myapp-frontend .
docker run -p 3000:80 myapp-frontend
```

### Database Migrations

To run database migrations:
```bash
docker-compose exec backend npx prisma migrate dev
```

To seed the database:
```bash
docker-compose exec backend npm run seed
```

## Production Deployment

1. **Set production environment variables**
2. **Use production-ready secrets**
3. **Configure proper CORS settings**
4. **Set up SSL/TLS certificates**
5. **Use a reverse proxy (nginx/traefik)**

## Troubleshooting

### Common Issues

1. **Port conflicts:** Make sure ports 3000, 5000, and 5432 are available
2. **Database connection:** Ensure PostgreSQL is running and accessible
3. **Build failures:** Check that all required files are present
4. **Environment variables:** Verify all required variables are set

### Logs

View logs for specific services:
```bash
docker-compose logs backend
docker-compose logs frontend
docker-compose logs postgres
```

### Reset Everything

To completely reset the application:
```bash
docker-compose down -v
docker-compose up --build
```

## API Endpoints

- `GET /health` - Health check
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration
- `GET /api/dashboard/stats` - Dashboard statistics (protected)

## Security Features

- Helmet.js for security headers
- Rate limiting
- CORS configuration
- JWT authentication
- Password hashing with bcrypt
- Input validation with Zod

