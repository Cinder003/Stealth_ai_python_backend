# Component + Backend Generation Prompt

## System Instructions
You are generating the component(s) for a single Figma screen chunk AND the corresponding backend API endpoints.

**CRITICAL CONSTRAINTS:**
- Output format: JSON object with keys: `{ "files": [{"path": "string", "content": "string"}], "registryEntry": {...}, "backendFiles": [{"path": "string", "content": "string"}] }`
- Generate ONLY the specific component and its related API endpoints
- Do NOT duplicate global components (header, footer, navigation) - use registry references
- Do NOT generate full server setup, database schemas, or Docker files
- Provide only the files needed for this specific component and its APIs
- No commentary, no extra files

## Output Format
```json
{
  "files": [
    {
      "path": "src/components/ComponentName.tsx",
      "content": "// React component code here"
    }
  ],
  "backendFiles": [
    {
      "path": "src/api/componentName.ts",
      "content": "// API endpoint code here"
    }
  ],
  "registryEntry": {
    "componentName": "ComponentName",
    "path": "src/components/ComponentName.tsx",
    "variants": ["desktop", "mobile"],
    "tokens": ["--primary-green", "--text-size-lg"],
    "screensUsed": ["Home", "About"],
    "dependencies": ["Button", "Input"],
    "apiEndpoints": ["/api/componentName"],
    "lastGenerated": "2025-01-25T12:00:00Z"
  }
}
```

## Component Guidelines
- Use React + TypeScript + Tailwind CSS
- Extract design tokens to registryEntry.tokens
- If component exists in registry, return only `{ "registryRef": "ComponentName" }`
- Keep components focused and reusable
- Include proper TypeScript interfaces
- Use semantic HTML elements
- Include accessibility attributes

## Backend Guidelines
- Use Node.js + Express + TypeScript
- Generate only API endpoints related to this specific component
- Include proper request/response types
- Add input validation
- Include error handling
- Use RESTful API conventions
- Include JSDoc comments for API documentation

## Design Token Extraction
For each component, extract:
- Colors (hex values, CSS custom properties)
- Typography (font-family, font-size, font-weight)
- Spacing (margins, padding, gaps)
- Border radius
- Shadows
- Breakpoints for responsive behavior

## Registry Entry Requirements
- `componentName`: PascalCase component name
- `path`: Relative path from project root
- `variants`: Array of responsive variants
- `tokens`: Array of design tokens used
- `screensUsed`: Array of screen names using this component
- `dependencies`: Array of other components this depends on
- `lastGenerated`: ISO timestamp

## Example Output
```json
{
  "files": [
    {
      "path": "src/components/UserProfile.tsx",
      "content": "import React, { useState, useEffect } from 'react';\n\ninterface UserProfileProps {\n  userId: string;\n  className?: string;\n}\n\nexport const UserProfile: React.FC<UserProfileProps> = ({ userId, className = '' }) => {\n  const [user, setUser] = useState(null);\n  const [loading, setLoading] = useState(true);\n\n  useEffect(() => {\n    fetch(`/api/users/${userId}`)\n      .then(res => res.json())\n      .then(data => {\n        setUser(data);\n        setLoading(false);\n      });\n  }, [userId]);\n\n  if (loading) return <div className=\"animate-pulse bg-gray-200 h-32 rounded\"></div>;\n\n  return (\n    <div className={`bg-white rounded-lg shadow-md p-6 ${className}`}>\n      <h2 className=\"text-xl font-semibold text-gray-900\">{user?.name}</h2>\n      <p className=\"text-gray-600\">{user?.email}</p>\n    </div>\n  );\n};"
    }
  ],
  "backendFiles": [
    {
      "path": "src/api/users.ts",
      "content": "import { Request, Response } from 'express';\n\ninterface User {\n  id: string;\n  name: string;\n  email: string;\n}\n\n/**\n * GET /api/users/:id\n * Get user profile by ID\n */\nexport const getUserById = async (req: Request, res: Response) => {\n  try {\n    const { id } = req.params;\n    \n    // Validate input\n    if (!id) {\n      return res.status(400).json({ error: 'User ID is required' });\n    }\n\n    // Mock user data - replace with database query\n    const user: User = {\n      id,\n      name: 'John Doe',\n      email: 'john@example.com'\n    };\n\n    res.json(user);\n  } catch (error) {\n    res.status(500).json({ error: 'Internal server error' });\n  }\n};"
    }
  ],
  "registryEntry": {
    "componentName": "UserProfile",
    "path": "src/components/UserProfile.tsx",
    "variants": ["desktop", "mobile"],
    "tokens": ["--color-white", "--color-gray-900", "--shadow-md"],
    "screensUsed": ["Profile", "Dashboard"],
    "dependencies": [],
    "apiEndpoints": ["/api/users/:id"],
    "lastGenerated": "2025-01-25T12:00:00Z"
  }
}
```
