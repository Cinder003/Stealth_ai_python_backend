#!/usr/bin/env python3
"""
Python example for using the Code Generation API
"""

import requests
import json
import os
from pathlib import Path


class CodeGenerator:
    """Client for the Code Generation API"""
    
    def __init__(self, base_url: str = "http://localhost:6000/api/v1"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def generate(
        self,
        prompt: str,
        code_type: str = "frontend",
        framework: str = None,
        production_ready: bool = False,
        include_tests: bool = False,
        styling: str = "tailwindcss",
        **kwargs
    ) -> dict:
        """
        Generate code based on prompt
        
        Args:
            prompt: Natural language description
            code_type: Type of code (frontend, backend, fullstack, component)
            framework: Framework to use (auto-detected if None)
            production_ready: Include production features
            include_tests: Include test files
            styling: CSS approach
            **kwargs: Additional parameters
            
        Returns:
            Response dictionary
        """
        payload = {
            "prompt": prompt,
            "code_type": code_type,
            "production_ready": production_ready,
            "include_tests": include_tests,
            "styling": styling,
            **kwargs
        }
        
        if framework:
            payload["framework"] = framework
        
        response = self.session.post(
            f"{self.base_url}/generate_code",
            json=payload
        )
        
        response.raise_for_status()
        return response.json()
    
    def save_files(self, result: dict, output_dir: str = "output"):
        """
        Save generated files to disk
        
        Args:
            result: API response
            output_dir: Directory to save files
        """
        if not result.get("success"):
            print("Generation failed:", result)
            return
        
        files = result.get("files", [])
        
        for file in files:
            file_path = Path(output_dir) / file["path"]
            
            # Create directory if needed
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(file["content"])
            
            print(f"✓ Created: {file_path} ({file['size_bytes']} bytes)")
        
        print(f"\n✅ Generated {len(files)} files in {output_dir}/")
        print(f"Total lines: {result.get('total_lines', 0)}")
        print(f"Generation time: {result.get('generation_time_seconds', 0):.2f}s")


def main():
    """Example usage"""
    
    # Initialize client
    client = CodeGenerator()
    
    # Example 1: Simple React component
    print("Example 1: Generating React button component...")
    print("-" * 50)
    
    result = client.generate(
        prompt="Create a modern button component with loading state and different variants",
        code_type="component",
        framework="react",
        styling="tailwindcss"
    )
    
    client.save_files(result, "output/example1")
    print("\n")
    
    # Example 2: Production React app
    print("Example 2: Generating production React app...")
    print("-" * 50)
    
    result = client.generate(
        prompt="Create a todo app with add, delete, and mark as complete functionality. Include dark mode.",
        code_type="frontend",
        framework="react",
        production_ready=True,
        include_tests=True,
        styling="tailwindcss"
    )
    
    client.save_files(result, "output/example2")
    print("\n")
    
    # Example 3: Node.js REST API
    print("Example 3: Generating Node.js REST API...")
    print("-" * 50)
    
    result = client.generate(
        prompt="Create a REST API for managing books with CRUD operations",
        code_type="backend",
        framework="express",
        production_ready=True
    )
    
    client.save_files(result, "output/example3")
    print("\n")
    
    print("🎉 All examples completed!")
    print("\nCheck the output/ directory for generated code.")


if __name__ == "__main__":
    main()

