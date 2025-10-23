# Prompt Templates

This directory contains LLM prompt templates for code generation.

## Structure

- `base/` - Base system instructions and output formats
- `generation/` - Code generation prompts
  - `frontend/` - Frontend-specific prompts
  - `backend/` - Backend-specific prompts
- `templates/` - Reusable prompt components

## Usage

Prompts are built dynamically by the `PromptBuilder` helper class based on:
- Code type (frontend, backend, fullstack)
- Framework (React, Vue, Node.js, etc.)
- Production readiness requirements
- Test inclusion preferences

## Best Practices

1. **Be Specific**: Clearly specify the technology stack and requirements
2. **Include Context**: Provide enough context for the LLM to understand the task
3. **Request Structure**: Ask for explicit file paths and organized code structure
4. **Quality Standards**: Include quality requirements (error handling, tests, etc.)
5. **Output Format**: Specify the expected output format clearly

## Customization

You can customize prompts by modifying the `PromptBuilder` class in `app/helpers/prompt_builder.py`.

