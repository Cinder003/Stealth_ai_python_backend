# Production Fullstack Application Prompt Template

Generate a complete production-ready fullstack application with the following specifications:

## Technical Stack
- **Frontend**: React 18+ with TypeScript, Tailwind CSS
- **Backend**: Node.js 18+ with Express.js, TypeScript
- **Database**: PostgreSQL with Prisma ORM
- **Authentication**: JWT-based authentication
- **Deployment**: Docker containerization

## User Requirements
{user_prompt}

## Code Quality Standards

### 1. Frontend Requirements
- **Architecture**: Component-based with custom hooks
- **State Management**: React Context API or Zustand
- **Styling**: Tailwind CSS with responsive design
- **Type Safety**: Full TypeScript implementation
- **Performance**: Code splitting, lazy loading, memoization
- **Accessibility**: ARIA attributes, keyboard navigation, screen reader support
- **Error Handling**: Error boundaries, loading states, user feedback

### 2. Backend Requirements
- **Architecture**: RESTful API with proper separation of concerns
- **Security**: Helmet.js, CORS, rate limiting, input validation
- **Authentication**: JWT with refresh tokens
- **Database**: Prisma ORM with migrations and seeding
- **Logging**: Structured logging with Winston
- **Testing**: Unit and integration tests
- **Documentation**: OpenAPI/Swagger documentation

### 3. Integration Requirements
- **API Contracts**: Shared TypeScript interfaces
- **Error Handling**: Consistent error responses
- **Validation**: Input validation on both ends
- **Environment**: Environment variable management
- **Docker**: Multi-stage Docker builds

## Project Structure

```
project/
├── frontend/
│   ├── src/
│   │   ├── components/          # Reusable UI components
│   │   ├── pages/              # Page components
│   │   ├── hooks/              # Custom React hooks
│   │   ├── context/            # Context providers
│   │   ├── services/           # API service functions
│   │   ├── types/              # TypeScript interfaces
│   │   ├── utils/              # Utility functions
│   │   └── App.tsx             # Main app component
│   ├── package.json
│   ├── tailwind.config.js
│   └── Dockerfile
├── backend/
│   ├── src/
│   │   ├── routes/             # API routes
│   │   ├── controllers/        # Route controllers
│   │   ├── services/           # Business logic
│   │   ├── models/             # Data models
│   │   ├── middleware/         # Custom middleware
│   │   ├── utils/              # Utility functions
│   │   ├── types/              # TypeScript interfaces
│   │   └── server.ts           # Server entry point
│   ├── package.json
│   ├── prisma/
│   └── Dockerfile
├── shared/
│   └── types/                  # Shared TypeScript interfaces
├── docker-compose.yml
└── README.md
```

## Output Format

Structure your response as follows:

### Frontend Files
```
File: frontend/src/[path]/[filename].tsx
```tsx
// React component code
```

### Backend Files
```
File: backend/src/[path]/[filename].ts
```typescript
// Backend code
```

### Shared Types
```
File: shared/types/[filename].ts
```typescript
// Shared interfaces
```

### Configuration Files
```
File: [filename]
```
[configuration content]
```

## Code Standards

### Frontend Standards
- Use functional components with hooks
- Implement proper TypeScript interfaces
- Add comprehensive error handling
- Include loading states and user feedback
- Follow accessibility best practices
- Use semantic HTML elements
- Implement responsive design
- Add proper form validation

### Backend Standards
- Use async/await for all asynchronous operations
- Implement proper error handling middleware
- Add input validation and sanitization
- Use environment variables for configuration
- Implement proper logging
- Add rate limiting and security headers
- Follow RESTful API conventions
- Include comprehensive API documentation

### Integration Standards
- Ensure API contracts match between frontend and backend
- Use consistent error response formats
- Implement proper authentication flow
- Add environment variable validation
- Include Docker configuration for both services
- Add proper CORS configuration
- Implement proper database connection handling

## Additional Requirements

### 1. Authentication Flow
- User registration and login
- JWT token management
- Protected routes on frontend
- Authentication middleware on backend
- Password hashing and validation

### 2. Error Handling
- Global error boundaries in React
- Consistent error response format
- User-friendly error messages
- Proper HTTP status codes
- Error logging and monitoring

### 3. Performance
- Code splitting and lazy loading
- Database query optimization
- Caching strategies
- Image optimization
- Bundle size optimization

### 4. Security
- Input validation and sanitization
- XSS and CSRF protection
- Secure authentication
- Environment variable security
- Database security

### 5. Testing
- Unit tests for critical functions
- Integration tests for API endpoints
- Component testing for React
- Database testing
- End-to-end testing setup

## File Organization

1. **Start with shared types and interfaces**
2. **Create backend API endpoints and controllers**
3. **Implement frontend components and pages**
4. **Add authentication and authorization**
5. **Include configuration files**
6. **Add Docker and deployment files**
7. **Include documentation and setup instructions**

Generate the complete, production-ready fullstack application now:
