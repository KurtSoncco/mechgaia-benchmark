#!/usr/bin/env python3
"""
MechGAIA Local Testing Script

Run this BEFORE pushing to Render to catch import errors locally
"""

import sys
import subprocess
import os
from pathlib import Path


class LocalTest:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.warnings = 0
        
    def section(self, title):
        """Print section header"""
        print(f"\n{'='*80}")
        print(f"  {title}")
        print(f"{'='*80}\n")
    
    def success(self, msg):
        """Print success message"""
        print(f"✓ {msg}")
        self.passed += 1
    
    def error(self, msg):
        """Print error message"""
        print(f"✗ {msg}")
        self.failed += 1
    
    def warning(self, msg):
        """Print warning message"""
        print(f"⚠ {msg}")
        self.warnings += 1
    
    def test_python_version(self):
        """Test 1: Check Python version"""
        self.section("1. Python Version Check")
        
        version = sys.version_info
        print(f"Python {version.major}.{version.minor}.{version.micro}")
        print(f"Executable: {sys.executable}\n")
        
        if version.major >= 3 and version.minor >= 13:
            self.success(f"Python {version.major}.{version.minor} meets requirement (>=3.13)")
        else:
            self.error(f"Python {version.major}.{version.minor} is below 3.13 requirement")
    
    def test_venv(self):
        """Test 2: Check if venv is activated"""
        self.section("2. Virtual Environment Check")
        
        in_venv = hasattr(sys, 'real_prefix') or (
            hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
        )
        
        if in_venv:
            self.success(f"Virtual environment active: {sys.prefix}")
        else:
            self.warning("No virtual environment detected (not required, but recommended)")
    
    def test_pyproject(self):
        """Test 3: Validate pyproject.toml"""
        self.section("3. pyproject.toml Validation")
        
        try:
            import tomllib
            with open('pyproject.toml', 'rb') as f:
                config = tomllib.load(f)
            
            self.success("pyproject.toml is valid TOML")
            print(f"  Project: {config['project']['name']}")
            print(f"  Version: {config['project']['version']}")
            print(f"  Python requirement: {config['project']['requires-python']}")
            print(f"  Dependencies: {len(config['project']['dependencies'])} packages\n")
            
            # Check for critical deps
            deps = config['project']['dependencies']
            critical = ['fastapi', 'uvicorn', 'agentbeats']
            missing = [d for d in critical if not any(d in dep for dep in deps)]
            
            if missing:
                self.error(f"Missing critical dependencies: {missing}")
            else:
                self.success("All critical dependencies declared in pyproject.toml")
                
        except FileNotFoundError:
            self.error("pyproject.toml not found!")
        except Exception as e:
            self.error(f"Error reading pyproject.toml: {e}")
    
    def test_imports(self):
        """Test 4: Test critical imports"""
        self.section("4. Critical Imports Test")
        
        critical_imports = [
            ('fastapi', 'FastAPI'),
            ('uvicorn', None),
            ('agentbeats', None),
            ('litellm', None),
            ('flask', 'Flask'),
            ('pandas', None),
            ('numpy', None),
        ]
        
        optional_imports = [
            ('anthropic', 'Anthropic'),  # Optional - commented out in pyproject.toml
        ]
        
        for module, item in critical_imports:
            try:
                if item:
                    exec(f"from {module} import {item}")
                    self.success(f"from {module} import {item}")
                else:
                    exec(f"import {module}")
                    mod = sys.modules[module]
                    version = getattr(mod, '__version__', 'unknown')
                    self.success(f"import {module} (v{version})")
            except ImportError as e:
                self.error(f"{module}: {e}")
            except Exception as e:
                self.error(f"{module}: {type(e).__name__}: {e}")
        
        # Test optional imports
        print("\nOptional imports (not required):")
        for module, item in optional_imports:
            try:
                if item:
                    exec(f"from {module} import {item}")
                    self.success(f"from {module} import {item} (optional)")
                else:
                    exec(f"import {module}")
                    mod = sys.modules[module]
                    version = getattr(mod, '__version__', 'unknown')
                    self.success(f"import {module} (optional, v{version})")
            except ImportError:
                self.warning(f"{module} not installed (optional)")
            except Exception as e:
                self.warning(f"{module}: {type(e).__name__}: {e} (optional)")
    
    def test_syntax(self):
        """Test 5: Check agentbeats_main.py syntax"""
        self.section("5. agentbeats_main.py Syntax Check")
        
        if not Path('agentbeats_main.py').exists():
            self.error("agentbeats_main.py not found!")
            return
        
        try:
            with open('agentbeats_main.py', 'r') as f:
                code = f.read()
            compile(code, 'agentbeats_main.py', 'exec')
            self.success("agentbeats_main.py has valid Python syntax")
        except SyntaxError as e:
            self.error(f"Syntax error in agentbeats_main.py: {e}")
    
    def test_app_import(self):
        """Test 6: Import agentbeats_main and check app object"""
        self.section("6. FastAPI App Import Test")
        
        sys.path.insert(0, '.')
        try:
            import agentbeats_main
            self.success("agentbeats_main module imported successfully")
            
            if hasattr(agentbeats_main, 'app'):
                app = agentbeats_main.app
                self.success(f"app object found: {type(app)}")
                
                # Check for routes
                if hasattr(app, 'routes'):
                    print(f"  Routes ({len(app.routes)}):")
                    for route in app.routes:
                        if hasattr(route, 'path'):
                            methods = getattr(route, 'methods', set())
                            print(f"    {methods} {route.path}")
            else:
                self.error("app object not found in agentbeats_main module")
                
        except ModuleNotFoundError as e:
            self.error(f"Cannot import agentbeats_main: {e}")
        except SyntaxError as e:
            self.error(f"Syntax error in agentbeats_main: {e}")
        except Exception as e:
            self.error(f"Error importing agentbeats_main: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
    
    def test_render_yaml(self):
        """Test 7: Validate render.yaml"""
        self.section("7. render.yaml Validation")
        
        if not Path('render.yaml').exists():
            self.error("render.yaml not found!")
            return
        
        try:
            import yaml
            with open('render.yaml', 'r') as f:
                config = yaml.safe_load(f)
            
            self.success("render.yaml is valid YAML")
            service = config['services'][0]
            
            print(f"  Service name: {service.get('name')}")
            print(f"  Environment: {service.get('env')}")
            print(f"  Python version: {service.get('pythonVersion')}")
            print(f"  Build command: {service.get('buildCommand')}")
            print(f"  Start command: {service.get('startCommand')}\n")
            
            # Check critical fields
            py_version = service.get('pythonVersion')
            # YAML may parse as string or number, so check both
            if py_version == '3.13' or py_version == 3.13 or str(py_version) == '3.13':
                self.success("Python 3.13 specified in render.yaml")
            elif py_version:
                self.warning(f"Python version is {py_version} (expected 3.13)")
            else:
                self.warning("Python version not specified in render.yaml")
            
            if 'pip install' in service.get('buildCommand', '') or 'uv' in service.get('buildCommand', ''):
                self.success("Build command uses pip/uv install")
            else:
                self.warning(f"Unexpected build command: {service.get('buildCommand')}")
                
        except FileNotFoundError:
            self.error("render.yaml not found!")
        except Exception as e:
            self.error(f"Error reading render.yaml: {e}")
    
    def run_all(self):
        """Run all tests"""
        print("\n" + "="*80)
        print("  MECHGAIA LOCAL TEST SUITE")
        print("="*80)
        
        self.test_python_version()
        self.test_venv()
        self.test_pyproject()
        self.test_imports()
        self.test_syntax()
        self.test_app_import()
        self.test_render_yaml()
        
        # Summary
        self.section("TEST SUMMARY")
        print(f"Passed:  {self.passed} ✓")
        print(f"Failed:  {self.failed} ✗")
        print(f"Warnings: {self.warnings} ⚠\n")
        
        if self.failed > 0:
            print("❌ TESTS FAILED - Do not push to Render yet!")
            return False
        elif self.warnings > 0:
            print("⚠️  TESTS PASSED with warnings - Review before pushing")
            return True
        else:
            print("✅ ALL TESTS PASSED - Safe to push to Render!")
            return True


if __name__ == '__main__':
    tester = LocalTest()
    success = tester.run_all()
    sys.exit(0 if success else 1)

