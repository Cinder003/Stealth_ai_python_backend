# Production React Application Prompt Template

Generate a production-ready React application with the following features:

## Technical Stack
- React 18+ with functional components and hooks
- Modern JavaScript (ES6+) or TypeScript
- Component-based architecture
- State management (Context API, Redux, or Zustand as appropriate)

## Code Quality Requirements

### 1. Error Handling
- Error boundaries for component error catching
- Proper error states in components
- User-friendly error messages

### 2. Loading States
- Loading indicators for async operations
- Skeleton screens where appropriate
- Optimistic UI updates

### 3. Performance
- React.memo for expensive components
- useMemo and useCallback for optimization
- Code splitting with React.lazy
- Image optimization

### 4. Accessibility
- Semantic HTML elements
- ARIA attributes where needed
- Keyboard navigation support
- Screen reader compatibility
- Color contrast compliance

### 5. Type Safety
- PropTypes or TypeScript interfaces
- Input validation
- Type checking for API responses

### 6. Styling
- Consistent styling approach
- Responsive design (mobile-first)
- Theme support (if applicable)
- CSS-in-JS or CSS modules

## Project Structure

```
src/
├── components/          # Reusable UI components
├── pages/              # Page components
├── hooks/              # Custom React hooks
├── context/            # Context providers
├── utils/              # Utility functions
├── services/           # API service functions
├── styles/             # Global styles
├── types/              # TypeScript types
├── constants/          # Constants and config
└── App.jsx            # Main app component
```

## Additional Files
- package.json with all dependencies
- .gitignore
- README.md with setup instructions
- .env.example for environment variables

## Code Standards
- Consistent naming conventions (camelCase for functions, PascalCase for components)
- Meaningful variable and function names
- DRY (Don't Repeat Yourself) principle
- Single Responsibility Principle
- Proper code comments

