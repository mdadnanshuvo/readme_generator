import os
import re
from pathlib import Path
import ast
import importlib.util
from typing import Dict, List, Optional, Union
from datetime import datetime

class ProjectAnalyzer:
    """
    Analyzes Python projects to extract comprehensive information for README generation.
    Includes code analysis, dependency tracking, and project structure mapping.
    """
    
    def __init__(self, project_path: str = '.'):
        self.project_path = project_path
        self.exclude_dirs = {'.git', '__pycache__', 'venv', 'env', 'node_modules', '.pytest_cache', 'build', 'dist'}
    
    def analyze_python_file(self, file_path: str) -> Dict:
        """
        Performs deep analysis of Python files to extract metadata, docstrings, and structure.
        
        Args:
            file_path: Path to the Python file to analyze
            
        Returns:
            Dict containing file analysis information
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            tree = ast.parse(content)
            
            # Extract imports for dependency tracking
            imports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imports.extend(n.name for n in node.names)
                elif isinstance(node, ast.ImportFrom):
                    imports.append(node.module)
            
            return {
                'name': os.path.basename(file_path),
                'docstring': ast.get_docstring(tree) or '',
                'functions': [
                    {
                        'name': node.name,
                        'docstring': ast.get_docstring(node) or '',
                        'args': [arg.arg for arg in node.args.args],
                        'returns': self._extract_return_type(node)
                    }
                    for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
                ],
                'classes': [
                    {
                        'name': node.name,
                        'docstring': ast.get_docstring(node) or '',
                        'methods': [
                            {
                                'name': method.name,
                                'docstring': ast.get_docstring(method) or ''
                            }
                            for method in node.body if isinstance(method, ast.FunctionDef)
                        ]
                    }
                    for node in ast.walk(tree) if isinstance(node, ast.ClassDef)
                ],
                'imports': imports
            }
        except Exception as e:
            return {'error': f"Error analyzing {file_path}: {str(e)}"}
    
    def _extract_return_type(self, node: ast.FunctionDef) -> str:
        """Extract return type annotation if present."""
        if node.returns:
            return ast.unparse(node.returns)
        return ''
    
    def analyze_project(self) -> Dict:
        """
        Performs comprehensive project analysis including structure, dependencies,
        and documentation extraction.
        
        Returns:
            Dict containing complete project analysis
        """
        project_info = {
            'name': os.path.basename(os.path.abspath(self.project_path)),
            'structure': [],
            'python_files': [],
            'dependencies': {
                'requirements': self._parse_requirements(),
                'imports': set()
            },
            'documentation': [],
            'tests': [],
            'license': self._get_license_info(),
            'git_info': self._get_git_info()
        }
        
        for root, dirs, files in os.walk(self.project_path):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs]
            
            rel_path = os.path.relpath(root, self.project_path)
            level = rel_path.count(os.sep)
            indent = '    ' * level
            
            if rel_path != '.':
                project_info['structure'].append(f"{indent}- {os.path.basename(root)}/")
            
            for file in files:
                file_path = os.path.join(root, file)
                subindent = '    ' * (level + 1)
                project_info['structure'].append(f"{subindent}- {file}")
                
                if file.endswith('.py'):
                    if 'test' in file.lower():
                        project_info['tests'].append(file_path)
                    else:
                        project_info['python_files'].append(file_path)
                    
                    analysis = self.analyze_python_file(file_path)
                    if 'error' not in analysis:
                        project_info['dependencies']['imports'].update(analysis['imports'])
                        project_info['documentation'].append(analysis)
        
        return project_info

    def _parse_requirements(self) -> List[str]:
        """Parse project dependencies from requirements files."""
        requirements = []
        req_files = ['requirements.txt', 'Pipfile', 'setup.py']
        
        for req_file in req_files:
            req_path = os.path.join(self.project_path, req_file)
            if os.path.exists(req_path):
                with open(req_path, 'r', encoding='utf-8') as f:
                    requirements.extend(line.strip() for line in f if line.strip() 
                                     and not line.startswith('#'))
        
        return requirements
    
    def _get_license_info(self) -> Optional[str]:
        """Extract license information if available."""
        license_files = ['LICENSE', 'LICENSE.txt', 'LICENSE.md']
        for license_file in license_files:
            license_path = os.path.join(self.project_path, license_file)
            if os.path.exists(license_path):
                with open(license_path, 'r', encoding='utf-8') as f:
                    return f.read()
        return None
    
    def _get_git_info(self) -> Dict:
        """Extract git repository information if available."""
        git_info = {'has_git': False, 'remote_url': None}
        git_path = os.path.join(self.project_path, '.git')
        
        if os.path.exists(git_path):
            git_info['has_git'] = True
            config_path = os.path.join(git_path, 'config')
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    content = f.read()
                    url_match = re.search(r'url = (.+)', content)
                    if url_match:
                        git_info['remote_url'] = url_match.group(1)
        
        return git_info

class ReadmeGenerator:
    """
    Generates professional README.md files with comprehensive project documentation.
    """
    
    def __init__(self, project_info: Dict):
        self.project_info = project_info
        
    def generate(self) -> str:
        """
        Generates a complete README.md file with all project information.
        
        Returns:
            str: Complete README content in Markdown format
        """
        sections = [
            self._generate_header(),
            self._generate_description(),
            self._generate_installation(),
            self._generate_usage(),
            self._generate_api_documentation(),
            self._generate_project_structure(),
            self._generate_testing(),
            self._generate_contributing(),
            self._generate_license(),
            self._generate_footer()
        ]
        
        return '\n\n'.join(section for section in sections if section)
    
    def _generate_header(self) -> str:
        """Generate project header with badges."""
        header = [
            f"# {self.project_info['name']}",
            "",
            "[![Python](https://img.shields.io/badge/python-3.6%2B-blue.svg)]",
            "[![License](https://img.shields.io/badge/license-MIT-green.svg)]"
        ]
        
        if self.project_info['git_info']['has_git']:
            header.append("[![GitHub](https://img.shields.io/badge/github-repo-black.svg)]")
        
        return '\n'.join(header)
    
    def _generate_description(self) -> str:
        """Generate project description from main module docstring."""
        if self.project_info['documentation']:
            main_module = self.project_info['documentation'][0]
            if main_module['docstring']:
                return f"## Description\n\n{main_module['docstring']}"
        return ""
    
    def _generate_installation(self) -> str:
        """Generate installation instructions."""
        install = ["## Installation", "", "```bash", "pip install -r requirements.txt", "```"]
        
        if self.project_info['dependencies']['requirements']:
            install.extend([
                "",
                "### Dependencies",
                "",
                "* " + "\n* ".join(self.project_info['dependencies']['requirements'])
            ])
        
        return '\n'.join(install)
    
    def _generate_usage(self) -> str:
        """Generate usage examples from main module."""
        usage = ["## Usage", ""]
        
        if self.project_info['documentation']:
            main_module = self.project_info['documentation'][0]
            if main_module['functions']:
                usage.extend([
                    "```python",
                    f"from {self.project_info['name'].lower()} import {main_module['functions'][0]['name']}",
                    "",
                    "# Example usage",
                    f"{main_module['functions'][0]['name']}()",
                    "```"
                ])
        
        return '\n'.join(usage)
    
    def _generate_api_documentation(self) -> str:
        """Generate API documentation from analyzed Python files."""
        if not self.project_info['documentation']:
            return ""
        
        api_docs = ["## API Documentation", ""]
        
        for module in self.project_info['documentation']:
            api_docs.extend([
                f"### {module['name']}",
                "",
                module['docstring'] if module['docstring'] else "No module description available.",
                ""
            ])
            
            if module['classes']:
                api_docs.extend(self._document_classes(module['classes']))
            
            if module['functions']:
                api_docs.extend(self._document_functions(module['functions']))
        
        return '\n'.join(api_docs)
    
    def _document_classes(self, classes: List[Dict]) -> List[str]:
        """Generate class documentation."""
        docs = []
        for cls in classes:
            docs.extend([
                f"#### class {cls['name']}",
                "",
                cls['docstring'] if cls['docstring'] else "No class description available.",
                "",
                "Methods:",
                ""
            ])
            
            for method in cls['methods']:
                docs.extend([
                    f"- `{method['name']}`",
                    f"  - {method['docstring']}" if method['docstring'] else "  - No description available.",
                    ""
                ])
        
        return docs
    
    def _document_functions(self, functions: List[Dict]) -> List[str]:
        """Generate function documentation."""
        docs = []
        for func in functions:
            args_str = ', '.join(func['args'])
            returns_str = f" -> {func['returns']}" if func['returns'] else ""
            
            docs.extend([
                f"#### {func['name']}({args_str}){returns_str}",
                "",
                func['docstring'] if func['docstring'] else "No function description available.",
                ""
            ])
        
        return docs
    
    def _generate_project_structure(self) -> str:
        """Generate project structure tree."""
        return "## Project Structure\n\n```\n" + '\n'.join(self.project_info['structure']) + "\n```"
    
    def _generate_testing(self) -> str:
        """Generate testing information."""
        if not self.project_info['tests']:
            return ""
        
        return "\n".join([
            "## Testing",
            "",
            "Run the tests using:",
            "",
            "```bash",
            "python -m pytest",
            "```"
        ])
    
    def _generate_contributing(self) -> str:
        """Generate contributing guidelines."""
        return "\n".join([
            "## Contributing",
            "",
            "1. Fork the repository",
            "2. Create your feature branch (`git checkout -b feature/AmazingFeature`)",
            "3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)",
            "4. Push to the branch (`git push origin feature/AmazingFeature`)",
            "5. Open a Pull Request"
        ])
    
    def _generate_license(self) -> str:
        """Generate license information."""
        if self.project_info['license']:
            return f"## License\n\n{self.project_info['license']}"
        return "## License\n\nThis project is licensed under the MIT License - see the LICENSE file for details."
    
    def _generate_footer(self) -> str:
        """Generate footer with generation timestamp."""
        return f"\n---\nGenerated by README Generator on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

def main(project_path: str = '.') -> None:
    """
    Main function to analyze project and generate README.
    
    Args:
        project_path: Path to the project root directory
    """
    # Analyze project
    analyzer = ProjectAnalyzer(project_path)
    project_info = analyzer.analyze_project()
    
    # Generate README
    generator = ReadmeGenerator(project_info)
    readme_content = generator.generate()
    
    # Save README
    readme_path = os.path.join(project_path, 'README.md')
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"README.md generated successfully at {readme_path}")

if __name__ == "__main__":
    main()