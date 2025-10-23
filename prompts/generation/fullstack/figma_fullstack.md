# Production Fullstack Application from Figma Design

Generate a complete production-ready fullstack application based on the provided Figma design with the following specifications:

## Technical Stack
- **Frontend**: React 18+ with TypeScript, Tailwind CSS
- **Backend**: Node.js 18+ with Express.js, TypeScript
- **Database**: PostgreSQL with Prisma ORM
- **Authentication**: JWT-based authentication
- **Deployment**: Docker containerization

## Figma Design Analysis
{figma_analysis}

## Design Data
```json
{figma_json}
```

## User Requirements
{user_message}

## Code Quality Standards

### 1. Frontend Requirements
- **Design Fidelity**: Match Figma design pixel-perfectly
- **Responsive Design**: Mobile-first approach with breakpoints
- **Component Architecture**: Reusable components based on design system
- **Styling**: Tailwind CSS with custom design tokens
- **Type Safety**: Full TypeScript implementation
- **Performance**: Optimized images, lazy loading, code splitting
- **Accessibility**: ARIA attributes, keyboard navigation, screen reader support
- **Animation**: Smooth transitions and micro-interactions

### 2. Backend Requirements
- **API Design**: RESTful endpoints matching frontend needs
- **Security**: Helmet.js, CORS, rate limiting, input validation
- **Authentication**: JWT with refresh tokens
- **Database**: Prisma ORM with proper relationships
- **File Handling**: Image upload and processing
- **Logging**: Structured logging with Winston
- **Testing**: Unit and integration tests
- **Documentation**: OpenAPI/Swagger documentation

### 3. Design System Requirements
- **Color Palette**: Extract and implement design colors
- **Typography**: Implement design typography scale
- **Spacing**: Consistent spacing system
- **Components**: Reusable UI components
- **Icons**: Icon system implementation
- **Images**: Optimized image handling

## Project Structure

```
project/
├── frontend/
│   ├── src/
│   │   ├── components/          # Design system components
│   │   │   ├── ui/             # Base UI components
│   │   │   ├── layout/         # Layout components
│   │   │   └── forms/          # Form components
│   │   ├── pages/              # Page components
│   │   ├── hooks/              # Custom React hooks
│   │   ├── context/            # Context providers
│   │   ├── services/           # API service functions
│   │   ├── types/              # TypeScript interfaces
│   │   ├── utils/              # Utility functions
│   │   ├── styles/             # Global styles and design tokens
│   │   └── App.tsx             # Main app component
│   ├── public/
│   │   └── images/             # Optimized images from Figma
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

### Design System
```
File: frontend/src/styles/design-tokens.ts
```typescript
// Design tokens extracted from Figma
```

### Frontend Components
```
File: frontend/src/components/[path]/[filename].tsx
```tsx
// React component matching Figma design
```

### Backend API
```
File: backend/src/[path]/[filename].ts
```typescript
// Backend API implementation
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

## Design Implementation Guidelines

### 1. Color System
- Extract primary, secondary, and accent colors from Figma
- Implement color variants (light, dark, hover states)
- Create Tailwind CSS custom color palette
- Ensure proper contrast ratios for accessibility

### 2. Typography
- Implement font families from Figma
- Create typography scale (headings, body, captions)
- Implement responsive font sizes
- Add proper line heights and letter spacing

### 3. Spacing System
- Extract spacing values from Figma
- Implement consistent margin and padding
- Create responsive spacing utilities
- Follow 8px grid system

### 4. Component Implementation
- Create reusable components based on Figma components
- Implement proper prop interfaces
- Add hover and focus states
- Ensure responsive behavior
- Add loading and error states

### 5. Layout Implementation
- Implement responsive grid system
- Create flexible layouts
- Handle different screen sizes
- Implement proper breakpoints

## Code Standards

### Frontend Standards
- Match Figma design pixel-perfectly
- Use semantic HTML elements
- Implement proper TypeScript interfaces
- Add comprehensive error handling
- Include loading states and animations
- Follow accessibility best practices
- Use Tailwind CSS for styling
- Implement responsive design

### Backend Standards
- Create API endpoints matching frontend needs
- Implement proper error handling
- Add input validation and sanitization
- Use environment variables for configuration
- Implement proper logging
- Add rate limiting and security headers
- Follow RESTful API conventions
- Include comprehensive API documentation

### Integration Standards
- Ensure API contracts match frontend requirements
- Use consistent error response formats
- Implement proper authentication flow
- Add environment variable validation
- Include Docker configuration
- Add proper CORS configuration
- Implement proper database relationships

## Additional Requirements

### 1. Image Handling
- Extract and optimize images from Figma
- Implement responsive image loading
- Add proper alt text for accessibility
- Use modern image formats (WebP, AVIF)

### 2. Animation and Interactions
- Implement smooth transitions
- Add micro-interactions
- Create loading animations
- Implement hover effects
- Add focus indicators

### 3. Performance
- Optimize images and assets
- Implement lazy loading
- Use code splitting
- Minimize bundle size
- Implement caching strategies

### 4. Accessibility
- Ensure proper color contrast
- Implement keyboard navigation
- Add screen reader support
- Use semantic HTML
- Implement focus management

## File Organization

1. **Start with design system and tokens**
2. **Create base UI components**
3. **Implement layout components**
4. **Create page components**
5. **Implement backend API endpoints**
6. **Add authentication and authorization**
7. **Include configuration files**
8. **Add Docker and deployment files**
9. **Include documentation and setup instructions**

Generate the complete, production-ready fullstack application matching the Figma design:
