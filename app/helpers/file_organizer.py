"""
File Organizer
Handles file organization and project structure management
"""

import os
import shutil
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class OrganizationStrategy(Enum):
    """File organization strategy enumeration"""
    FRAMEWORK = "framework"
    TYPE = "type"
    FEATURE = "feature"
    MODULE = "module"
    CUSTOM = "custom"


@dataclass
class FileInfo:
    """Information about a file"""
    path: str
    name: str
    extension: str
    size: int
    language: str
    framework: Optional[str] = None
    feature: Optional[str] = None
    module: Optional[str] = None


@dataclass
class OrganizationResult:
    """Result of file organization"""
    success: bool
    organized_files: List[Tuple[str, str]]  # (old_path, new_path)
    created_directories: List[str]
    errors: List[str]
    warnings: List[str]


class FileOrganizer:
    """Handles file organization and project structure management"""
    
    def __init__(self):
        self.framework_patterns = {
            'react': ['.jsx', '.tsx', '.js', '.ts'],
            'vue': ['.vue', '.js', '.ts'],
            'angular': ['.ts', '.js', '.html', '.scss'],
            'nodejs': ['.js', '.ts', '.json'],
            'python': ['.py'],
            'fastapi': ['.py'],
            'django': ['.py', '.html', '.css'],
            'flask': ['.py', '.html', '.css']
        }
        
        self.file_type_patterns = {
            'components': ['.jsx', '.tsx', '.vue'],
            'pages': ['.jsx', '.tsx', '.vue', '.html'],
            'styles': ['.css', '.scss', '.sass', '.less'],
            'scripts': ['.js', '.ts', '.py'],
            'config': ['.json', '.yaml', '.yml', '.toml', '.ini'],
            'tests': ['test_', '_test.', '.spec.', '.test.'],
            'docs': ['.md', '.txt', '.rst'],
            'assets': ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico']
        }
    
    def organize_project(
        self,
        project_path: str,
        strategy: OrganizationStrategy = OrganizationStrategy.FRAMEWORK,
        create_directories: bool = True,
        move_files: bool = False,
        custom_rules: Optional[Dict[str, Any]] = None
    ) -> OrganizationResult:
        """Organize project files according to strategy"""
        try:
            project_path = Path(project_path)
            if not project_path.exists():
                return OrganizationResult(
                    success=False,
                    organized_files=[],
                    created_directories=[],
                    errors=[f"Project path does not exist: {project_path}"],
                    warnings=[]
                )
            
            # Get all files
            files = self._get_project_files(project_path)
            
            # Organize based on strategy
            if strategy == OrganizationStrategy.FRAMEWORK:
                result = self._organize_by_framework(files, project_path, create_directories, move_files)
            elif strategy == OrganizationStrategy.TYPE:
                result = self._organize_by_type(files, project_path, create_directories, move_files)
            elif strategy == OrganizationStrategy.FEATURE:
                result = self._organize_by_feature(files, project_path, create_directories, move_files)
            elif strategy == OrganizationStrategy.MODULE:
                result = self._organize_by_module(files, project_path, create_directories, move_files)
            elif strategy == OrganizationStrategy.CUSTOM:
                result = self._organize_by_custom(files, project_path, create_directories, move_files, custom_rules)
            else:
                return OrganizationResult(
                    success=False,
                    organized_files=[],
                    created_directories=[],
                    errors=[f"Unknown organization strategy: {strategy}"],
                    warnings=[]
                )
            
            return result
            
        except Exception as e:
            return OrganizationResult(
                success=False,
                organized_files=[],
                created_directories=[],
                errors=[f"Organization failed: {str(e)}"],
                warnings=[]
            )
    
    def create_project_structure(
        self,
        project_path: str,
        framework: str,
        features: List[str] = None
    ) -> OrganizationResult:
        """Create a standard project structure for a framework"""
        try:
            project_path = Path(project_path)
            
            if features is None:
                features = ['components', 'pages', 'styles', 'scripts', 'tests']
            
            # Create base directories
            directories = self._get_framework_directories(framework, features)
            
            created_dirs = []
            for directory in directories:
                dir_path = project_path / directory
                dir_path.mkdir(parents=True, exist_ok=True)
                created_dirs.append(str(dir_path))
            
            # Create framework-specific files
            framework_files = self._get_framework_files(framework)
            created_files = []
            
            for file_path, content in framework_files.items():
                full_path = project_path / file_path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(full_path, 'w') as f:
                    f.write(content)
                
                created_files.append((str(full_path), str(full_path)))
            
            return OrganizationResult(
                success=True,
                organized_files=created_files,
                created_directories=created_dirs,
                errors=[],
                warnings=[]
            )
            
        except Exception as e:
            return OrganizationResult(
                success=False,
                organized_files=[],
                created_directories=[],
                errors=[f"Structure creation failed: {str(e)}"],
                warnings=[]
            )
    
    def analyze_project_structure(self, project_path: str) -> Dict[str, Any]:
        """Analyze project structure and provide insights"""
        try:
            project_path = Path(project_path)
            files = self._get_project_files(project_path)
            
            analysis = {
                "total_files": len(files),
                "total_size": sum(f.size for f in files),
                "languages": {},
                "frameworks": {},
                "file_types": {},
                "structure_issues": [],
                "recommendations": []
            }
            
            # Analyze languages
            for file_info in files:
                language = file_info.language
                analysis["languages"][language] = analysis["languages"].get(language, 0) + 1
            
            # Analyze frameworks
            for file_info in files:
                framework = self._detect_framework(file_info)
                if framework:
                    analysis["frameworks"][framework] = analysis["frameworks"].get(framework, 0) + 1
            
            # Analyze file types
            for file_info in files:
                file_type = self._classify_file_type(file_info)
                analysis["file_types"][file_type] = analysis["file_types"].get(file_type, 0) + 1
            
            # Check for structure issues
            analysis["structure_issues"] = self._check_structure_issues(files, project_path)
            
            # Generate recommendations
            analysis["recommendations"] = self._generate_recommendations(analysis)
            
            return analysis
            
        except Exception as e:
            return {
                "error": f"Analysis failed: {str(e)}",
                "total_files": 0,
                "total_size": 0,
                "languages": {},
                "frameworks": {},
                "file_types": {},
                "structure_issues": [],
                "recommendations": []
            }
    
    def _get_project_files(self, project_path: Path) -> List[FileInfo]:
        """Get all files in project with metadata"""
        files = []
        
        for file_path in project_path.rglob('*'):
            if file_path.is_file():
                try:
                    file_info = FileInfo(
                        path=str(file_path),
                        name=file_path.name,
                        extension=file_path.suffix.lower(),
                        size=file_path.stat().st_size,
                        language=self._detect_language(file_path)
                    )
                    files.append(file_info)
                except Exception:
                    # Skip files that can't be processed
                    continue
        
        return files
    
    def _detect_language(self, file_path: Path) -> str:
        """Detect programming language from file"""
        extension = file_path.suffix.lower()
        
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.vue': 'vue',
            '.html': 'html',
            '.css': 'css',
            '.scss': 'scss',
            '.sass': 'sass',
            '.less': 'less',
            '.json': 'json',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.md': 'markdown',
            '.txt': 'text',
            '.sql': 'sql'
        }
        
        return language_map.get(extension, 'unknown')
    
    def _detect_framework(self, file_info: FileInfo) -> Optional[str]:
        """Detect framework from file information"""
        for framework, extensions in self.framework_patterns.items():
            if file_info.extension in extensions:
                return framework
        
        return None
    
    def _classify_file_type(self, file_info: FileInfo) -> str:
        """Classify file type"""
        for file_type, patterns in self.file_type_patterns.items():
            for pattern in patterns:
                if pattern.startswith('.'):
                    if file_info.extension == pattern:
                        return file_type
                else:
                    if pattern in file_info.name:
                        return file_type
        
        return 'other'
    
    def _organize_by_framework(
        self,
        files: List[FileInfo],
        project_path: Path,
        create_directories: bool,
        move_files: bool
    ) -> OrganizationResult:
        """Organize files by framework"""
        organized_files = []
        created_directories = []
        errors = []
        warnings = []
        
        # Group files by framework
        framework_groups = {}
        for file_info in files:
            framework = self._detect_framework(file_info)
            if framework:
                if framework not in framework_groups:
                    framework_groups[framework] = []
                framework_groups[framework].append(file_info)
            else:
                # Unknown framework files
                if 'unknown' not in framework_groups:
                    framework_groups['unknown'] = []
                framework_groups['unknown'].append(file_info)
        
        # Create directories and move files
        for framework, framework_files in framework_groups.items():
            framework_dir = project_path / framework
            
            if create_directories:
                framework_dir.mkdir(exist_ok=True)
                created_directories.append(str(framework_dir))
            
            for file_info in framework_files:
                if move_files:
                    new_path = framework_dir / file_info.name
                    try:
                        shutil.move(file_info.path, str(new_path))
                        organized_files.append((file_info.path, str(new_path)))
                    except Exception as e:
                        errors.append(f"Failed to move {file_info.path}: {str(e)}")
                else:
                    # Just record the intended organization
                    new_path = framework_dir / file_info.name
                    organized_files.append((file_info.path, str(new_path)))
        
        return OrganizationResult(
            success=len(errors) == 0,
            organized_files=organized_files,
            created_directories=created_directories,
            errors=errors,
            warnings=warnings
        )
    
    def _organize_by_type(
        self,
        files: List[FileInfo],
        project_path: Path,
        create_directories: bool,
        move_files: bool
    ) -> OrganizationResult:
        """Organize files by type"""
        organized_files = []
        created_directories = []
        errors = []
        warnings = []
        
        # Group files by type
        type_groups = {}
        for file_info in files:
            file_type = self._classify_file_type(file_info)
            if file_type not in type_groups:
                type_groups[file_type] = []
            type_groups[file_type].append(file_info)
        
        # Create directories and move files
        for file_type, type_files in type_groups.items():
            type_dir = project_path / file_type
            
            if create_directories:
                type_dir.mkdir(exist_ok=True)
                created_directories.append(str(type_dir))
            
            for file_info in type_files:
                if move_files:
                    new_path = type_dir / file_info.name
                    try:
                        shutil.move(file_info.path, str(new_path))
                        organized_files.append((file_info.path, str(new_path)))
                    except Exception as e:
                        errors.append(f"Failed to move {file_info.path}: {str(e)}")
                else:
                    # Just record the intended organization
                    new_path = type_dir / file_info.name
                    organized_files.append((file_info.path, str(new_path)))
        
        return OrganizationResult(
            success=len(errors) == 0,
            organized_files=organized_files,
            created_directories=created_directories,
            errors=errors,
            warnings=warnings
        )
    
    def _organize_by_feature(
        self,
        files: List[FileInfo],
        project_path: Path,
        create_directories: bool,
        move_files: bool
    ) -> OrganizationResult:
        """Organize files by feature"""
        organized_files = []
        created_directories = []
        errors = []
        warnings = []
        
        # Group files by feature (simplified implementation)
        feature_groups = {}
        for file_info in files:
            # Extract feature from path or name
            feature = self._extract_feature(file_info)
            if feature not in feature_groups:
                feature_groups[feature] = []
            feature_groups[feature].append(file_info)
        
        # Create directories and move files
        for feature, feature_files in feature_groups.items():
            feature_dir = project_path / feature
            
            if create_directories:
                feature_dir.mkdir(exist_ok=True)
                created_directories.append(str(feature_dir))
            
            for file_info in feature_files:
                if move_files:
                    new_path = feature_dir / file_info.name
                    try:
                        shutil.move(file_info.path, str(new_path))
                        organized_files.append((file_info.path, str(new_path)))
                    except Exception as e:
                        errors.append(f"Failed to move {file_info.path}: {str(e)}")
                else:
                    # Just record the intended organization
                    new_path = feature_dir / file_info.name
                    organized_files.append((file_info.path, str(new_path)))
        
        return OrganizationResult(
            success=len(errors) == 0,
            organized_files=organized_files,
            created_directories=created_directories,
            errors=errors,
            warnings=warnings
        )
    
    def _organize_by_module(
        self,
        files: List[FileInfo],
        project_path: Path,
        create_directories: bool,
        move_files: bool
    ) -> OrganizationResult:
        """Organize files by module"""
        organized_files = []
        created_directories = []
        errors = []
        warnings = []
        
        # Group files by module (simplified implementation)
        module_groups = {}
        for file_info in files:
            # Extract module from path or name
            module = self._extract_module(file_info)
            if module not in module_groups:
                module_groups[module] = []
            module_groups[module].append(file_info)
        
        # Create directories and move files
        for module, module_files in module_groups.items():
            module_dir = project_path / module
            
            if create_directories:
                module_dir.mkdir(exist_ok=True)
                created_directories.append(str(module_dir))
            
            for file_info in module_files:
                if move_files:
                    new_path = module_dir / file_info.name
                    try:
                        shutil.move(file_info.path, str(new_path))
                        organized_files.append((file_info.path, str(new_path)))
                    except Exception as e:
                        errors.append(f"Failed to move {file_info.path}: {str(e)}")
                else:
                    # Just record the intended organization
                    new_path = module_dir / file_info.name
                    organized_files.append((file_info.path, str(new_path)))
        
        return OrganizationResult(
            success=len(errors) == 0,
            organized_files=organized_files,
            created_directories=created_directories,
            errors=errors,
            warnings=warnings
        )
    
    def _organize_by_custom(
        self,
        files: List[FileInfo],
        project_path: Path,
        create_directories: bool,
        move_files: bool,
        custom_rules: Optional[Dict[str, Any]]
    ) -> OrganizationResult:
        """Organize files by custom rules"""
        if not custom_rules:
            return OrganizationResult(
                success=False,
                organized_files=[],
                created_directories=[],
                errors=["No custom rules provided"],
                warnings=[]
            )
        
        # Implement custom organization logic
        # This would be based on the provided custom_rules
        return OrganizationResult(
            success=True,
            organized_files=[],
            created_directories=[],
            errors=[],
            warnings=["Custom organization not fully implemented"]
        )
    
    def _extract_feature(self, file_info: FileInfo) -> str:
        """Extract feature name from file"""
        # Simple feature extraction based on directory structure
        path_parts = Path(file_info.path).parts
        
        # Look for common feature indicators
        for part in path_parts:
            if part in ['components', 'pages', 'features', 'modules']:
                return part
        
        # Default to 'general'
        return 'general'
    
    def _extract_module(self, file_info: FileInfo) -> str:
        """Extract module name from file"""
        # Simple module extraction
        if 'test' in file_info.name.lower():
            return 'tests'
        elif 'config' in file_info.name.lower():
            return 'config'
        elif 'util' in file_info.name.lower():
            return 'utils'
        else:
            return 'main'
    
    def _get_framework_directories(self, framework: str, features: List[str]) -> List[str]:
        """Get standard directories for a framework"""
        base_dirs = {
            'react': ['src', 'public', 'src/components', 'src/pages', 'src/styles'],
            'vue': ['src', 'public', 'src/components', 'src/views', 'src/assets'],
            'angular': ['src', 'src/app', 'src/app/components', 'src/app/services'],
            'nodejs': ['src', 'tests', 'config'],
            'python': ['src', 'tests', 'config'],
            'fastapi': ['app', 'tests', 'config'],
            'django': ['app', 'tests', 'static', 'templates']
        }
        
        directories = base_dirs.get(framework, ['src', 'tests'])
        
        # Add feature-specific directories
        for feature in features:
            if feature == 'components':
                directories.append('src/components')
            elif feature == 'pages':
                directories.append('src/pages')
            elif feature == 'styles':
                directories.append('src/styles')
            elif feature == 'scripts':
                directories.append('src/scripts')
            elif feature == 'tests':
                directories.append('tests')
        
        return directories
    
    def _get_framework_files(self, framework: str) -> Dict[str, str]:
        """Get standard files for a framework"""
        files = {
            'react': {
                'package.json': '{\n  "name": "react-app",\n  "version": "1.0.0",\n  "dependencies": {\n    "react": "^18.0.0",\n    "react-dom": "^18.0.0"\n  }\n}',
                'src/App.js': 'import React from "react";\n\nfunction App() {\n  return (\n    <div className="App">\n      <h1>Hello World</h1>\n    </div>\n  );\n}\n\nexport default App;'
            },
            'vue': {
                'package.json': '{\n  "name": "vue-app",\n  "version": "1.0.0",\n  "dependencies": {\n    "vue": "^3.0.0"\n  }\n}',
                'src/App.vue': '<template>\n  <div id="app">\n    <h1>Hello World</h1>\n  </div>\n</template>\n\n<script>\nexport default {\n  name: "App"\n}\n</script>'
            },
            'nodejs': {
                'package.json': '{\n  "name": "nodejs-app",\n  "version": "1.0.0",\n  "main": "index.js",\n  "dependencies": {\n    "express": "^4.0.0"\n  }\n}',
                'index.js': 'const express = require("express");\nconst app = express();\n\napp.get("/", (req, res) => {\n  res.send("Hello World");\n});\n\napp.listen(3000, () => {\n  console.log("Server running on port 3000");\n});'
            },
            'python': {
                'requirements.txt': 'flask==2.0.0\n',
                'main.py': 'from flask import Flask\n\napp = Flask(__name__)\n\n@app.route("/")\ndef hello():\n    return "Hello World"\n\nif __name__ == "__main__":\n    app.run()'
            }
        }
        
        return files.get(framework, {})
    
    def _check_structure_issues(self, files: List[FileInfo], project_path: Path) -> List[str]:
        """Check for common structure issues"""
        issues = []
        
        # Check for files in root directory
        root_files = [f for f in files if Path(f.path).parent == project_path]
        if len(root_files) > 5:
            issues.append("Too many files in root directory")
        
        # Check for missing test files
        test_files = [f for f in files if 'test' in f.name.lower()]
        if len(test_files) == 0:
            issues.append("No test files found")
        
        # Check for missing configuration files
        config_files = [f for f in files if f.extension in ['.json', '.yaml', '.yml', '.toml']]
        if len(config_files) == 0:
            issues.append("No configuration files found")
        
        return issues
    
    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        # Language recommendations
        if 'python' in analysis['languages']:
            recommendations.append("Consider adding a requirements.txt file")
        
        if 'javascript' in analysis['languages']:
            recommendations.append("Consider adding a package.json file")
        
        # Framework recommendations
        if 'react' in analysis['frameworks']:
            recommendations.append("Consider organizing components in src/components/")
        
        if 'vue' in analysis['frameworks']:
            recommendations.append("Consider organizing components in src/components/")
        
        # Structure recommendations
        if analysis['total_files'] > 50:
            recommendations.append("Consider organizing files into subdirectories")
        
        return recommendations
