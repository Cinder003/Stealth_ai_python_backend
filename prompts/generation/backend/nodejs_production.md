# Production Node.js Backend Prompt Template

Generate a production-ready Node.js backend application with the following features:

## Technical Stack
- Node.js 18+ with Express.js or similar framework
- Modern JavaScript (ES6+) or TypeScript
- RESTful API design
- Environment-based configuration

## Code Quality Requirements

### 1. Error Handling
- Global error handling middleware
- Async error wrapper
- Proper HTTP status codes
- Detailed error logging
- User-friendly error responses

### 2. Validation
- Input validation middleware (e.g., Joi, express-validator)
- Request body validation
- Query parameter validation
- Sanitization to prevent XSS/injection

### 3. Security
- Helmet.js for security headers
- CORS configuration
- Rate limiting
- Request size limits
- Environment variable validation
- SQL injection prevention
- XSS protection

### 4. Authentication & Authorization
- JWT or session-based authentication
- Password hashing (bcrypt)
- Protected routes middleware
- Role-based access control (if needed)

### 5. Logging & Monitoring
- Structured logging (Winston, Pino)
- Request logging
- Error logging
- Performance monitoring
- Health check endpoint

### 6. Database
- Database connection pooling
- Query optimization
- Transaction support
- Migration files (if applicable)
- Seeding (if applicable)

### 7. API Documentation
- OpenAPI/Swagger documentation
- Endpoint descriptions
- Request/response examples
- Authentication documentation

## Project Structure

```
src/
├── routes/             # API routes
├── controllers/        # Route controllers
├── services/           # Business logic
├── models/            # Data models
├── middleware/        # Custom middleware
├── utils/             # Utility functions
├── config/            # Configuration files
├── validators/        # Input validators
├── constants/         # Constants
└── server.js          # Server entry point
```

## Additional Files
- package.json with all dependencies
- .gitignore
- README.md with API documentation
- .env.example
- docker-compose.yml (optional)

## Code Standards
- Consistent naming conventions
- Async/await for asynchronous operations
- Proper error handling
- RESTful API conventions
- Meaningful variable and function names
- Comprehensive comments
- Environment variables for configuration

## API Best Practices
- Versioned API (e.g., /api/v1/)
- Consistent response format
- Proper HTTP methods (GET, POST, PUT, DELETE, PATCH)
- Pagination for list endpoints
- Filtering and sorting support
- Request validation
- Response compression

