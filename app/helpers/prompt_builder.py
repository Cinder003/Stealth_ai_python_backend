"""Prompt Builder - Constructs prompts for code generation"""

import json
import logging
from typing import Optional, Dict, Any
from app.models.enums import CodeType, Framework

logger = logging.getLogger(__name__)


class PromptBuilder:
    """Build prompts for code generation"""
    
    SYSTEM_INSTRUCTIONS = """You are an expert software engineer specializing in generating production-ready code.
Generate clean, well-structured, and fully functional code based on user requirements.
Always include proper error handling, input validation, and follow best practices.
Format your response with clear file paths and code blocks."""
    
    def build_frontend_prompt(
        self,
        user_prompt: str,
        framework: Framework = Framework.REACT,
        production_ready: bool = False,
        include_tests: bool = False,
        styling: str = "tailwindcss"
    ) -> str:
        """
        Build prompt for frontend code generation
        
        Args:
            user_prompt: User's natural language description
            framework: Frontend framework
            production_ready: Whether to include production features
            include_tests: Whether to include tests
            styling: CSS approach
            
        Returns:
            Complete prompt for LLM
        """
        framework_instructions = self._get_framework_instructions(framework)
        
        prompt = f"""{self.SYSTEM_INSTRUCTIONS}

## Task
Generate a complete {framework.value} application based on the following requirements:

{user_prompt}

## Technical Requirements
- Framework: {framework.value}
- Styling: {styling}
- Production Ready: {'Yes' if production_ready else 'No'}
- Include Tests: {'Yes' if include_tests else 'No'}

## Output Format
Structure your response as follows:

File: <relative/path/to/file>
```<language>
<code content>
```

Repeat for each file needed.

## Code Quality Standards
{"- Implement comprehensive error handling and error boundaries" if production_ready else ""}
{"- Add PropTypes or TypeScript types" if production_ready else ""}
{"- Include loading and error states" if production_ready else ""}
{"- Add proper accessibility attributes (ARIA)" if production_ready else ""}
{"- Optimize for performance (memoization, lazy loading)" if production_ready else ""}
{"- Add unit tests using Jest and React Testing Library" if include_tests else ""}
- Use modern {framework.value} best practices
- Write clean, readable, and maintainable code
- Add helpful comments for complex logic
- Follow consistent naming conventions

## File Structure
Create a proper project structure with:
- Component files in src/components/
- Utilities in src/utils/
- Styles appropriately organized
- Configuration files (package.json, etc.)
{"- Test files in src/__tests__/" if include_tests else ""}
{"- README.md with setup instructions" if production_ready else ""}

Generate the complete, working application now:
"""
        return prompt.strip()
    
    def build_backend_prompt(
        self,
        user_prompt: str,
        framework: Framework = Framework.NODEJS,
        production_ready: bool = False,
        include_tests: bool = False
    ) -> str:
        """
        Build prompt for backend code generation
        
        Args:
            user_prompt: User's natural language description
            framework: Backend framework
            production_ready: Whether to include production features
            include_tests: Whether to include tests
            
        Returns:
            Complete prompt for LLM
        """
        prompt = f"""{self.SYSTEM_INSTRUCTIONS}

## Task
Generate a complete {framework.value} backend application based on the following requirements:

{user_prompt}

## Technical Requirements
- Framework: {framework.value}
- Production Ready: {'Yes' if production_ready else 'No'}
- Include Tests: {'Yes' if include_tests else 'No'}

## Output Format
Structure your response as follows:

File: <relative/path/to/file>
```<language>
<code content>
```

Repeat for each file needed.

## Code Quality Standards
{"- Implement comprehensive error handling middleware" if production_ready else ""}
{"- Add input validation and sanitization" if production_ready else ""}
{"- Include authentication and authorization" if production_ready else ""}
{"- Add request logging and monitoring" if production_ready else ""}
{"- Implement rate limiting" if production_ready else ""}
{"- Add API documentation (Swagger/OpenAPI)" if production_ready else ""}
{"- Include integration and unit tests" if include_tests else ""}
- Use environment variables for configuration
- Follow RESTful API design principles
- Write clean, readable, and maintainable code
- Add helpful comments for complex logic
- Use TypeScript (if applicable)

## File Structure
Create a proper project structure with:
- Routes/controllers in src/routes/ or src/controllers/
- Business logic in src/services/
- Database models in src/models/
- Middleware in src/middleware/
- Utilities in src/utils/
- Configuration files (package.json, .env.example, etc.)
{"- Test files appropriately organized" if include_tests else ""}
{"- README.md with API documentation and setup instructions" if production_ready else ""}

Generate the complete, working application now:
"""
        return prompt.strip()
    
    def build_fullstack_prompt(
        self,
        user_prompt: str,
        frontend_framework: Framework = Framework.REACT,
        backend_framework: Framework = Framework.NODEJS,
        production_ready: bool = False,
        include_tests: bool = False,
        styling: str = "tailwindcss"
    ) -> str:
        """
        Build prompt for fullstack application generation
        
        Args:
            user_prompt: User's natural language description
            frontend_framework: Frontend framework
            backend_framework: Backend framework
            production_ready: Whether to include production features
            include_tests: Whether to include tests
            styling: CSS approach
            
        Returns:
            Complete prompt for LLM
        """
        prompt = f"""{self.SYSTEM_INSTRUCTIONS}

## Task
Generate a complete fullstack application with {frontend_framework.value} frontend and {backend_framework.value} backend based on the following requirements:

{user_prompt}

## Technical Requirements
- Frontend: {frontend_framework.value} with {styling}
- Backend: {backend_framework.value}
- Production Ready: {'Yes' if production_ready else 'No'}
- Include Tests: {'Yes' if include_tests else 'No'}

## Output Format
Structure your response as follows:

File: <relative/path/to/file>
```<language>
<code content>
```

Repeat for each file needed.

## Project Structure
Organize files clearly:
- frontend/ - All frontend code
- backend/ - All backend code
- Root configuration files (docker-compose.yml, etc.)

## Code Quality Standards
- Implement proper API integration between frontend and backend
- Add comprehensive error handling on both ends
- Use environment variables for configuration
- Follow best practices for both stacks
{"- Include proper authentication flow" if production_ready else ""}
{"- Add API documentation and setup instructions" if production_ready else ""}
{"- Include tests for both frontend and backend" if include_tests else ""}

Generate the complete, working fullstack application now:
"""
        return prompt.strip()
    
    def build_fullstack_production_prompt(
        self,
        user_prompt: str,
        frontend_framework: Framework = Framework.REACT,
        backend_framework: Framework = Framework.NODEJS,
        production_ready: bool = True,
        include_tests: bool = False,
        styling: str = "tailwindcss"
    ) -> str:
        """
        Build prompt for production fullstack application generation
        
        Args:
            user_prompt: User's natural language description
            frontend_framework: Frontend framework
            backend_framework: Backend framework
            include_tests: Whether to include tests
            styling: CSS approach
            
        Returns:
            Complete prompt for LLM
        """
        # Load production fullstack prompt template
        try:
            with open("prompts/generation/fullstack/production_fullstack.md", "r") as f:
                template = f.read()
        except FileNotFoundError:
            # Fallback to inline template
            template = self._get_production_fullstack_template()
        
        # Replace placeholders
        prompt = template.replace("{user_prompt}", user_prompt)
        prompt = prompt.replace("{frontend_framework}", frontend_framework.value)
        prompt = prompt.replace("{backend_framework}", backend_framework.value)
        prompt = prompt.replace("{styling}", styling)
        prompt = prompt.replace("{include_tests}", "Yes" if include_tests else "No")
        
        return prompt.strip()
    
    def build_figma_fullstack_prompt(
        self,
        user_message: str,
        figma_analysis: Dict[str, Any],
        figma_json: Dict[str, Any],
        frontend_framework: Framework = Framework.REACT,
        backend_framework: Framework = Framework.NODEJS,
        include_tests: bool = False,
        styling: str = "tailwindcss"
    ) -> str:
        """
        Build prompt for Figma-based fullstack application generation
        
        Args:
            user_message: User's additional requirements
            figma_analysis: Analysis of Figma design
            figma_json: Figma JSON data
            frontend_framework: Frontend framework
            backend_framework: Backend framework
            include_tests: Whether to include tests
            styling: CSS approach
            
        Returns:
            Complete prompt for LLM
        """
        # Load Figma fullstack prompt template
        try:
            with open("prompts/generation/fullstack/figma_fullstack.md", "r") as f:
                template = f.read()
        except FileNotFoundError:
            # Fallback to inline template
            template = self._get_figma_fullstack_template()
        
        # Replace placeholders
        prompt = template.replace("{user_message}", user_message or "")
        prompt = prompt.replace("{figma_analysis}", json.dumps(figma_analysis, indent=2))
        prompt = prompt.replace("{figma_json}", json.dumps(figma_json, indent=2))
        prompt = prompt.replace("{frontend_framework}", frontend_framework.value)
        prompt = prompt.replace("{backend_framework}", backend_framework.value)
        prompt = prompt.replace("{styling}", styling)
        prompt = prompt.replace("{include_tests}", "Yes" if include_tests else "No")
        
        return prompt.strip()
    
    def _get_production_fullstack_template(self) -> str:
        """Fallback production fullstack template"""
        return """# Production Fullstack Application

Generate a complete production-ready fullstack application with the following specifications:

## User Requirements
{user_prompt}

## Technical Stack
- Frontend: {frontend_framework} with {styling}
- Backend: {backend_framework}
- Database: PostgreSQL with Prisma ORM
- Authentication: JWT-based
- Deployment: Docker

## Code Quality Standards
- Production-ready code with proper error handling
- TypeScript for type safety
- Comprehensive testing
- Security best practices
- Performance optimization
- Accessibility compliance

Generate the complete fullstack application now:"""
    
    def _get_figma_fullstack_template(self) -> str:
        """Fallback Figma fullstack template"""
        return """# Production Fullstack Application from Figma Design

Generate a complete production-ready fullstack application based on the provided Figma design:

## User Requirements
{user_message}

## Figma Design Data
```json
{figma_json}
```

## Technical Stack
- Frontend: {frontend_framework} with {styling}
- Backend: {backend_framework}
- Database: PostgreSQL with Prisma ORM
- Authentication: JWT-based
- Deployment: Docker

## Design Implementation
- Match Figma design pixel-perfectly
- Implement responsive design
- Extract design tokens (colors, typography, spacing)
- Create reusable components
- Optimize images and assets

Generate the complete fullstack application matching the Figma design:"""
    
    def build_component_prompt(
        self,
        user_prompt: str,
        framework: Framework = Framework.REACT,
        styling: str = "tailwindcss"
    ) -> str:
        """
        Build prompt for single component generation
        
        Args:
            user_prompt: Component description
            framework: Framework to use
            styling: Styling approach
            
        Returns:
            Complete prompt for LLM
        """
        prompt = f"""{self.SYSTEM_INSTRUCTIONS}

## Task
Generate a {framework.value} component based on the following requirements:

{user_prompt}

## Requirements
- Framework: {framework.value}
- Styling: {styling}
- Make it reusable and production-ready
- Add PropTypes or TypeScript types
- Include proper accessibility attributes

## Output Format
File: src/components/ComponentName.{self._get_extension(framework)}
```{self._get_language(framework)}
<component code>
```

Generate the component now:
"""
        return prompt.strip()
    
    def _get_framework_instructions(self, framework: Framework) -> str:
        """Get framework-specific instructions"""
        instructions = {
            Framework.REACT: "Use functional components with hooks. Use modern React patterns.",
            Framework.REACT_TYPESCRIPT: "Use functional components with TypeScript. Add proper type definitions.",
            Framework.VUE: "Use Vue 3 Composition API with script setup syntax.",
            Framework.ANGULAR: "Use Angular latest version with TypeScript.",
            Framework.NEXT: "Use Next.js 13+ with App Router and Server Components where appropriate.",
            Framework.NODEJS: "Use Express.js with async/await. Use ES6+ syntax.",
            Framework.EXPRESS: "Use Express.js with proper middleware and routing.",
            Framework.NEST: "Use NestJS with decorators and dependency injection.",
        }
        return instructions.get(framework, "Follow framework best practices.")
    
    def _get_extension(self, framework: Framework) -> str:
        """Get file extension for framework"""
        ext_map = {
            Framework.REACT: "jsx",
            Framework.REACT_TYPESCRIPT: "tsx",
            Framework.VUE: "vue",
            Framework.ANGULAR: "ts",
            Framework.NEXT: "jsx",
            Framework.NODEJS: "js",
            Framework.EXPRESS: "js",
            Framework.NEST: "ts",
        }
        return ext_map.get(framework, "js")
    
    def _get_language(self, framework: Framework) -> str:
        """Get language identifier for code blocks"""
        lang_map = {
            Framework.REACT: "jsx",
            Framework.REACT_TYPESCRIPT: "tsx",
            Framework.VUE: "vue",
            Framework.ANGULAR: "typescript",
            Framework.NEXT: "jsx",
            Framework.NODEJS: "javascript",
            Framework.EXPRESS: "javascript",
            Framework.NEST: "typescript",
        }
        return lang_map.get(framework, "javascript")
    
    def build_prompt(
        self,
        user_prompt: str,
        code_type: CodeType,
        framework: Optional[Framework] = None,
        production_ready: bool = False,
        include_tests: bool = False,
        **kwargs
    ) -> str:
        """
        Build appropriate prompt based on code type
        
        Args:
            user_prompt: User's description
            code_type: Type of code to generate
            framework: Framework to use
            production_ready: Production features flag
            include_tests: Include tests flag
            **kwargs: Additional arguments
            
        Returns:
            Complete prompt
        """
        # ALWAYS use fullstack prompts for better integration and context
        if code_type == CodeType.FRONTEND:
            # Use fullstack prompt but focus on frontend
            return self.build_fullstack_production_prompt(
                user_prompt=f"Create a frontend application: {user_prompt}",
                frontend_framework=framework or Framework.REACT,
                backend_framework=Framework.NODEJS,  # Default backend
                production_ready=production_ready,
                include_tests=include_tests,
                styling=kwargs.get('styling', 'tailwindcss')
            )
        elif code_type == CodeType.BACKEND:
            # Use fullstack prompt but focus on backend
            return self.build_fullstack_production_prompt(
                user_prompt=f"Create a backend API: {user_prompt}",
                frontend_framework=Framework.REACT,  # Default frontend
                backend_framework=framework or Framework.NODEJS,
                production_ready=production_ready,
                include_tests=include_tests,
                styling=kwargs.get('styling', 'tailwindcss')
            )
        elif code_type == CodeType.FULLSTACK:
            return self.build_fullstack_production_prompt(
                user_prompt,
                kwargs.get('frontend_framework', Framework.REACT),
                framework or Framework.NODEJS,
                production_ready,
                include_tests,
                kwargs.get('styling', 'tailwindcss')
            )
        elif code_type == CodeType.COMPONENT:
            # Use fullstack prompt for component (generates both component and supporting backend)
            return self.build_fullstack_production_prompt(
                user_prompt=f"Create a reusable component: {user_prompt}",
                frontend_framework=framework or Framework.REACT,
                backend_framework=Framework.NODEJS,
                production_ready=production_ready,
                include_tests=include_tests,
                styling=kwargs.get('styling', 'tailwindcss')
            )
        else:
            # Default to fullstack prompt
            return self.build_fullstack_production_prompt(
                user_prompt,
                Framework.REACT,
                Framework.NODEJS,
                production_ready,
                include_tests,
                kwargs.get('styling', 'tailwindcss')
            )

