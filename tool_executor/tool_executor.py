import os
import sys
import subprocess
import importlib.util
import tempfile
import time
import json
import logging
import shutil
from pathlib import Path
from typing import Dict, Any, Optional

from virtual_env_manager import get_env_manager
from github_downloader import get_downloader
from dependency_parser import get_parser
from schema_validator import get_validator
from mongodb_connector import get_db_connector

logger = logging.getLogger(__name__)

class ToolExecutor:
    """Complete tool execution pipeline in isolated environment"""
    
    def __init__(self):
        self.env_manager = get_env_manager()
        self.downloader = get_downloader()
        self.parser = get_parser()
        self.validator = get_validator()
        self.db = get_db_connector()
    
    def execute_tool(self, tool_name: str, user_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Complete tool execution pipeline
        
        Args:
            tool_name: Name of the tool to execute
            user_input: User parameters from POST request
            
        Returns:
            Execution results
        """
        execution_start_time = time.time()
        env_info = None
        
        try:
            logger.info(f"🚀 Starting complete tool execution pipeline for: {tool_name}")
            logger.info("=" * 80)
            
            # STEP 1: Get tool details from database
            logger.info("📋 STEP 1: Fetching tool details from database...")
            tool_details = self.db.get_tool_details(tool_name)
            
            if not tool_details:
                return self._error_response(f"Tool '{tool_name}' not found in database")
            
            logger.info(f"✅ Tool found: {tool_details['description'][:100]}...")
            
            # STEP 2: Validate user input against schema
            logger.info("🔍 STEP 2: Validating user input against schema...")
            input_schema = tool_details.get("input_schema", {})
            validation_result = self.validator.validate_input(user_input, input_schema)
            
            if not validation_result["valid"]:
                return self._error_response(
                    f"Input validation failed: {validation_result['errors']}",
                    {"validation_errors": validation_result["errors"]}
                )
            
            validated_input = validation_result["data"]
            logger.info(f"✅ Input validation passed. Validated data: {validated_input}")
            
            # STEP 3: Create isolated virtual environment
            logger.info("🔨 STEP 3: Creating isolated virtual environment...")
            env_info = self.env_manager.create_isolated_environment(tool_name)
            logger.info(f"✅ Isolated environment created: {env_info['temp_base_dir']}")
            
            # STEP 4: Create Blueprint directory structure and copy BaseTool
            logger.info("📁 STEP 4: Setting up Blueprint directory structure...")
            blueprint_setup_result = self._setup_blueprint_structure(env_info)
            
            if not blueprint_setup_result["success"]:
                return self._error_response(
                    f"Blueprint setup failed: {blueprint_setup_result['message']}",
                    {"blueprint_error": blueprint_setup_result}
                )
            
            logger.info("✅ Blueprint structure created and BaseTool copied")
            
            # STEP 5: Download tool from GitHub
            logger.info("📥 STEP 5: Downloading tool from GitHub...")
            download_result = self.downloader.download_tool_from_github(
                tool_name, 
                env_info["tools_dir"]
            )
            
            if download_result["status"] != "success":
                return self._error_response(
                    f"Tool download failed: {download_result.get('message')}",
                    {"download_error": download_result}
                )
            
            tool_file_path = download_result["file_path"]
            logger.info(f"✅ Tool downloaded: {tool_file_path}")
            
            # STEP 6: Parse and install dependencies
            logger.info("📦 STEP 6: Parsing and installing dependencies...")
            dependencies = self.parser.extract_dependencies_from_file(tool_file_path)
            
            if dependencies:
                logger.info(f"📦 Installing {len(dependencies)} dependencies: {dependencies}")
                install_result = self._install_dependencies(dependencies, env_info)
                
                if not install_result["success"]:
                    return self._error_response(
                        f"Dependency installation failed: {install_result['message']}",
                        {"dependency_errors": install_result["errors"]}
                    )
                
                logger.info("✅ Dependencies installed successfully")
            else:
                logger.info("ℹ️ No dependencies to install")
            
            # STEP 7: Execute the tool
            logger.info("🚀 STEP 7: Executing tool in isolated environment...")
            execution_result = self._execute_tool_in_environment(
                tool_file_path, 
                validated_input, 
                env_info
            )
            
            if execution_result["status"] != "success":
                return self._error_response(
                    f"Tool execution failed: {execution_result.get('message')}",
                    {"execution_error": execution_result}
                )
            
            # STEP 8: Return success results
            execution_time = time.time() - execution_start_time
            logger.info(f"🎉 Tool execution completed successfully in {execution_time:.2f} seconds")
            
            return {
                "status": "success",
                "tool_name": tool_name,
                "result": execution_result["result"],
                "execution_info": {
                    "execution_time_seconds": round(execution_time, 2),
                    "validated_input": validated_input,
                    "dependencies_installed": dependencies,
                    "validation_warnings": validation_result.get("warnings", []),
                    "environment_path": env_info["temp_base_dir"],
                    "tool_file_size": download_result["file_size"],
                    "blueprint_setup": "success"
                },
                "message": f"Tool '{tool_name}' executed successfully"
            }
            
        except Exception as e:
            logger.error(f"❌ Critical error in tool execution pipeline: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return self._error_response(
                f"Critical execution error: {str(e)}",
                {"exception_type": type(e).__name__}
            )
            
        finally:
            # STEP 9: Always cleanup environment
            if env_info:
                logger.info("🧹 STEP 9: Cleaning up isolated environment...")
                try:
                    self.env_manager.cleanup_environment(env_info["temp_base_dir"])
                    logger.info("✅ Environment cleanup completed")
                except Exception as e:
                    logger.error(f"⚠️ Environment cleanup failed: {e}")
    
    def _setup_blueprint_structure(self, env_info: Dict[str, str]) -> Dict[str, Any]:
        """
        Create Blueprint directory structure and copy python_base_tool.py
        
        Creates: Blueprint/Templates/Tools/python_base_tool.py
        """
        try:
            logger.info("📁 Creating Blueprint directory structure...")
            
            # Create the exact Blueprint directory structure
            working_dir = Path(env_info["working_dir"])
            blueprint_dir = working_dir / "Blueprint" / "Templates" / "Tools"
            blueprint_dir.mkdir(parents=True, exist_ok=True)
            
            logger.info(f"📁 Created directory: {blueprint_dir}")
            
            # Find and copy python_base_tool.py from current directory
            current_dir = Path(__file__).parent
            source_base_tool = current_dir / "python_base_tool.py"
            target_base_tool = blueprint_dir / "python_base_tool.py"
            
            logger.info(f"🔍 Looking for python_base_tool.py at: {source_base_tool}")
            logger.info(f"📋 Target location: {target_base_tool}")
            
            if not source_base_tool.exists():
                return {
                    "success": False,
                    "message": f"python_base_tool.py not found at: {source_base_tool}"
                }
            
            # Copy the BaseTool file
            shutil.copy2(str(source_base_tool), str(target_base_tool))
            logger.info(f"📋 Copied BaseTool: {source_base_tool} → {target_base_tool}")
            
            # Create __init__.py files for proper Python module structure
            init_files = [
                working_dir / "Blueprint" / "__init__.py",
                working_dir / "Blueprint" / "Templates" / "__init__.py", 
                working_dir / "Blueprint" / "Templates" / "Tools" / "__init__.py"
            ]
            
            for init_file in init_files:
                init_file.write_text("")  # Create empty __init__.py
                logger.info(f"📄 Created __init__.py: {init_file}")
            
            # Verify the setup
            if target_base_tool.exists():
                file_size = target_base_tool.stat().st_size
                logger.info(f"✅ Blueprint setup completed - BaseTool file size: {file_size} bytes")
                
                # Verify content
                with open(target_base_tool, 'r', encoding='utf-8') as f:
                    content = f.read(200)
                    if "class BaseTool:" in content:
                        logger.info("✅ BaseTool class found in copied file")
                    else:
                        logger.warning("⚠️ BaseTool class not found in copied file")
                
                return {
                    "success": True,
                    "message": "Blueprint structure created successfully",
                    "base_tool_path": str(target_base_tool),
                    "base_tool_size": file_size
                }
            else:
                return {
                    "success": False,
                    "message": "BaseTool file was not copied successfully"
                }
                
        except Exception as e:
            logger.error(f"❌ Error setting up Blueprint structure: {e}")
            return {
                "success": False,
                "message": f"Blueprint setup error: {str(e)}"
            }
    
    def _install_dependencies(self, dependencies: list, env_info: Dict[str, str]) -> Dict[str, Any]:
        """Install dependencies in isolated environment"""
        
        install_results = {
            "success": True,
            "installed": [],
            "failed": [],
            "errors": []
        }
        
        pip_path = env_info["pip_path"]
        
        for package in dependencies:
            try:
                logger.info(f"📦 Installing: {package}")
                
                # Run pip install in isolated environment
                result = subprocess.run([
                    pip_path, "install", package
                ], 
                capture_output=True, 
                text=True, 
                timeout=30000  # 5 minute timeout per package
                )
                
                if result.returncode == 0:
                    install_results["installed"].append(package)
                    logger.info(f"✅ Successfully installed: {package}")
                else:
                    install_results["failed"].append(package)
                    install_results["errors"].append(f"{package}: {result.stderr}")
                    logger.error(f"❌ Failed to install {package}: {result.stderr}")
                    
            except subprocess.TimeoutExpired:
                install_results["failed"].append(package)
                install_results["errors"].append(f"{package}: Installation timeout")
                logger.error(f"❌ Installation timeout for: {package}")
                
            except Exception as e:
                install_results["failed"].append(package)
                install_results["errors"].append(f"{package}: {str(e)}")
                logger.error(f"❌ Installation error for {package}: {e}")
        
        # Consider success if at least some packages installed
        if install_results["failed"] and not install_results["installed"]:
            install_results["success"] = False
            install_results["message"] = f"All dependency installations failed"
        elif install_results["failed"]:
            install_results["message"] = f"Some dependencies failed: {install_results['failed']}"
        else:
            install_results["message"] = f"All {len(dependencies)} dependencies installed successfully"
        
        return install_results
    
    def _execute_tool_in_environment(self, tool_file_path: str, validated_input: Dict[str, Any], env_info: Dict[str, str]) -> Dict[str, Any]:
        """Execute the tool in isolated environment"""
        
        try:
            # Create execution script
            execution_script = self._create_execution_script(tool_file_path, validated_input, env_info)
            
            # Execute the script with UTF-8 environment
            python_path = env_info["python_path"]
            
            # Set UTF-8 environment variables
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'
            env['PYTHONUTF8'] = '1'
            
            logger.info("🔧 Executing tool with UTF-8 encoding...")
            result = subprocess.run([
                python_path, execution_script
            ],
            capture_output=True,
            text=True,
            timeout=30000,  # 5 minute timeout
            cwd=env_info["working_dir"],
            env=env,  # Pass UTF-8 environment
            encoding='utf-8',
            errors='replace'  # Replace problematic characters instead of failing
            )
            
            if result.returncode != 0:
                logger.error(f"❌ Tool execution failed: {result.stderr}")
                return {
                    "status": "error",
                    "message": f"Tool execution failed: {result.stderr}",
                    "stdout": result.stdout,
                    "stderr": result.stderr
                }
            
            # Parse result
            try:
                # Extract JSON from stdout
                output_lines = result.stdout.strip().split('\n')
                json_output = None
                
                # Find the last JSON block
                for line in reversed(output_lines):
                    if line.strip().startswith('{'):
                        try:
                            json_output = json.loads(line.strip())
                            break
                        except json.JSONDecodeError:
                            continue
                
                if json_output is None:
                    # Try to parse the entire stdout
                    json_output = json.loads(result.stdout.strip())
                
                return {
                    "status": "success",
                    "result": json_output,
                    "stdout": result.stdout,
                    "execution_time": "completed"
                }
                
            except json.JSONDecodeError as e:
                logger.error(f"❌ Failed to parse tool output as JSON: {e}")
                return {
                    "status": "error", 
                    "message": f"Tool output is not valid JSON: {e}",
                    "stdout": result.stdout,
                    "stderr": result.stderr
                }
                
        except subprocess.TimeoutExpired:
            return {
                "status": "error",
                "message": "Tool execution timeout (5 minutes)"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Tool execution error: {str(e)}"
            }
    
    def _create_execution_script(self, tool_file_path: str, validated_input: Dict[str, Any], env_info: Dict[str, str]) -> str:
            """Create COMPLETELY DYNAMIC execution script for ANY tool"""
            
            # 🔧 CRITICAL FIX: Use json.dumps for proper Python string generation
            import json
            
            # Convert validated_input to a properly escaped JSON string that can be embedded in Python code
            input_json_str = json.dumps(validated_input, ensure_ascii=False, separators=(',', ': '))
            
            # Escape the JSON string for embedding in Python triple quotes
            escaped_input_str = input_json_str.replace('\\', '\\\\').replace('"""', '\\"\\"\\"')
            
            script_content = f'''
import sys
import json
import importlib.util
import inspect
from pathlib import Path

def execute_tool():
    try:
        # Add working directory to Python path for Blueprint imports
        working_dir = r"{env_info["working_dir"]}"
        if working_dir not in sys.path:
            sys.path.insert(0, working_dir)
        
        print(f"DEBUG: Python path configured: {{working_dir}}")
        
        # Import the tool module
        tool_file_path = r"{tool_file_path}"
        spec = importlib.util.spec_from_file_location("tool_module", tool_file_path)
        tool_module = importlib.util.module_from_spec(spec)
        
        # Execute the module (this triggers all imports including BaseTool)
        spec.loader.exec_module(tool_module)
        print("DEBUG: Tool module loaded successfully")
        
        # DYNAMIC: Find ANY class that inherits from BaseTool
        tool_class = None
        all_classes = []
        
        for name in dir(tool_module):
            obj = getattr(tool_module, name)
            if isinstance(obj, type):
                all_classes.append(name)
                
                # Check if it has run_sync method and inherits from BaseTool
                if hasattr(obj, 'run_sync') and name != 'BaseTool':
                    try:
                        # Check inheritance via MRO (Method Resolution Order)
                        for base_class in obj.__mro__:
                            if base_class.__name__ == 'BaseTool':
                                tool_class = obj
                                print(f"DEBUG: Found tool class: {{name}}")
                                break
                        if tool_class:
                            break
                    except:
                        continue
        
        if not tool_class:
            raise Exception(f"No BaseTool subclass found. Classes found: {{all_classes}}")
        
        # DYNAMIC: Create tool instance
        print(f"DEBUG: Creating instance of {{tool_class.__name__}}")
        try:
            tool_instance = tool_class()
        except Exception as init_error1:
            try:
                tool_instance = tool_class(config=None)
            except Exception as init_error2:
                raise Exception(f"Tool instantiation failed. Error 1: {{init_error1}}, Error 2: {{init_error2}}")
        
        print("DEBUG: Tool instance created successfully")
        
        # 🔧 CRITICAL FIX: Parse JSON string instead of building Python dict
        input_json_string = """{escaped_input_str}"""
        validated_input = json.loads(input_json_string)
        
        print(f"DEBUG: Validated input: {{validated_input}}")
        
        run_sync_method = getattr(tool_instance, 'run_sync')
        signature = inspect.signature(run_sync_method)
        
        # Get parameter names (excluding 'self')
        param_names = [param.name for param in signature.parameters.values() if param.name != 'self']
        param_details = {{param.name: param for param in signature.parameters.values() if param.name != 'self'}}
        
        print(f"DEBUG: run_sync signature parameters: {{param_names}}")
        print(f"DEBUG: Parameter details: {{[(name, param.default, param.annotation) for name, param in param_details.items()]}}")
        
        # DYNAMIC: Map input to parameters based on actual signature
        call_args = {{}}
        call_kwargs = {{}}
        
        if len(param_names) == 0:
            # No parameters - call with no arguments
            print("DEBUG: Calling run_sync() with no parameters")
            result = tool_instance.run_sync()
            
        elif len(param_names) == 1:
            # Single parameter - pass entire validated_input
            param_name = param_names[0]
            print(f"DEBUG: Calling run_sync({{param_name}}={{validated_input}})")
            call_kwargs[param_name] = validated_input
            result = tool_instance.run_sync(**call_kwargs)
            
        else:
            # Multiple parameters - map each input field to matching parameter
            print("DEBUG: Multiple parameters detected - mapping fields dynamically")
            
            for param_name in param_names:
                param_info = param_details[param_name]
                
                if param_name in validated_input:
                    # Direct field match
                    call_kwargs[param_name] = validated_input[param_name]
                    print(f"DEBUG: Mapped {{param_name}} = {{validated_input[param_name]}}")
                    
                elif param_info.default != inspect.Parameter.empty:
                    # Parameter has default value - skip it
                    print(f"DEBUG: Using default for {{param_name}} = {{param_info.default}}")
                    
                else:
                    # Required parameter not found - try common mappings
                    if param_name in ['input_data', 'data']:
                        # Common pattern: run_sync(input_data, ...)
                        call_kwargs[param_name] = validated_input
                        print(f"DEBUG: Mapped {{param_name}} = entire validated_input")
                    elif param_name == 'llm_config':
                        # Common pattern: run_sync(..., llm_config)
                        call_kwargs[param_name] = None
                        print(f"DEBUG: Mapped {{param_name}} = None")
                    else:
                        print(f"WARNING: Required parameter '{{param_name}}' not found in input")
            
            print(f"DEBUG: Final call kwargs: {{call_kwargs}}")
            result = tool_instance.run_sync(**call_kwargs)
        
        print(f"DEBUG: Tool execution completed. Result type: {{type(result)}}")
        
        # Output result as JSON
        print(json.dumps(result, default=str, ensure_ascii=False))
        
    except Exception as e:
        import traceback
        error_result = {{
            "status": "error",
            "message": str(e),
            "traceback": traceback.format_exc()
        }}
        print(json.dumps(error_result, default=str, ensure_ascii=False))

if __name__ == "__main__":
    execute_tool()
    '''
        
            # Save script to temp directory
            script_path = Path(env_info["temp_files_dir"]) / "execute_tool.py"
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(script_content)
            
            logger.info(f"🔧 Generated execution script with properly escaped JSON input")
            logger.info(f"📋 Input JSON string length: {len(escaped_input_str)} characters")
            
            return str(script_path)
    
    def _error_response(self, message: str, details: Optional[Dict] = None) -> Dict[str, Any]:
        """Create standardized error response"""
        return {
            "status": "error",
            "message": message,
            "details": details or {},
            "timestamp": time.time()
        }

# Global executor instance
executor = None

def get_executor():
    """Get global executor instance"""
    global executor
    if executor is None:
        executor = ToolExecutor()
    return executor
