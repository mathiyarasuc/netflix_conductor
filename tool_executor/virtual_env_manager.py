import os
import sys
import tempfile
import subprocess
import shutil
import time
from pathlib import Path
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class VirtualEnvironmentManager:
    """Manages isolated virtual environments for tool execution"""
    
    def __init__(self):
        self.active_environments = {}
    
    def create_isolated_environment(self, tool_name: str) -> Dict[str, str]:
        """
        Create completely isolated virtual environment for tool execution
        
        Args:
            tool_name: Name of the tool (for unique directory naming)
            
        Returns:
            Dict with paths to python, pip, temp_dir, etc.
        """
        try:
            logger.info(f"🔨 Creating isolated environment for tool: {tool_name}")
            
            # Step 1: Create unique temporary directory
            temp_base_dir = tempfile.mkdtemp(
                prefix=f"isolated_tool_{tool_name}_", 
                suffix=f"_{int(time.time())}"
            )
            logger.info(f"📁 Created temp directory: {temp_base_dir}")
            
            # Step 2: Create virtual environment
            venv_dir = Path(temp_base_dir) / "tool_venv"
            logger.info(f"🐍 Creating virtual environment at: {venv_dir}")
            
            create_venv_command = [
                sys.executable,          # Current Python interpreter
                "-m", "venv",           # Use venv module
                str(venv_dir),          # Target directory
                "--clear"               # Clear if exists
            ]
            
            # Execute venv creation
            result = subprocess.run(
                create_venv_command,
                capture_output=True,
                text=True,
                timeout=120  
            )
            
            if result.returncode != 0:
                raise Exception(f"Failed to create virtual environment: {result.stderr}")
            
            logger.info("✅ Virtual environment created successfully")
            
            # Step 3: Get platform-specific Python paths
            if sys.platform == "win32":
                # Windows paths
                venv_python = venv_dir / "Scripts" / "python.exe"
                venv_pip = venv_dir / "Scripts" / "pip.exe"
            else:
                # Unix/Linux/Mac paths  
                venv_python = venv_dir / "bin" / "python"
                venv_pip = venv_dir / "bin" / "pip"
            
            logger.info(f"🐍 Virtual environment Python: {venv_python}")
            logger.info(f"📦 Virtual environment Pip: {venv_pip}")
            
            # Step 4: Verify virtual environment works
            logger.info("🔍 Verifying virtual environment...")
            
            # Test Python
            test_command = [str(venv_python), "--version"]
            test_result = subprocess.run(
                test_command,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if test_result.returncode != 0:
                raise Exception(f"Virtual environment verification failed: {test_result.stderr}")
            
            python_version = test_result.stdout.strip()
            logger.info(f"✅ Virtual environment verified: {python_version}")
            
            # Test pip
            pip_test = subprocess.run(
                [str(venv_pip), "--version"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if pip_test.returncode != 0:
                raise Exception(f"Pip verification failed: {pip_test.stderr}")
            
            logger.info(f"✅ Pip verified: {pip_test.stdout.strip()}")
            
            # Step 5: Create working directories
            work_dirs = [
                Path(temp_base_dir) / "scripts",      # For GitHub download script
                Path(temp_base_dir) / "tools",        # For downloaded tools
                Path(temp_base_dir) / "temp_files"    # For any temporary files
            ]
            
            for directory in work_dirs:
                directory.mkdir(parents=True, exist_ok=True)
                logger.info(f"📁 Created directory: {directory}")
            
            # Step 6: Build environment info
            env_info = {
                "temp_base_dir": temp_base_dir,
                "venv_dir": str(venv_dir),
                "python_path": str(venv_python),
                "pip_path": str(venv_pip),
                "scripts_dir": str(Path(temp_base_dir) / "scripts"),
                "tools_dir": str(Path(temp_base_dir) / "tools"),
                "temp_files_dir": str(Path(temp_base_dir) / "temp_files"),
                "working_dir": temp_base_dir,
                "platform": sys.platform,
                "created_at": time.time(),
                "tool_name": tool_name
            }
            
            # Store for tracking
            self.active_environments[temp_base_dir] = env_info
            
            logger.info(f"🎉 Isolated environment ready for {tool_name}")
            logger.info(f"📋 Environment paths:")
            for key, value in env_info.items():
                if key.endswith('_dir') or key.endswith('_path'):
                    logger.info(f"   {key}: {value}")
            
            return env_info
            
        except Exception as e:
            # Cleanup on failure
            if 'temp_base_dir' in locals():
                self.cleanup_environment(temp_base_dir)
            logger.error(f"❌ Failed to create isolated environment: {str(e)}")
            raise Exception(f"Failed to create isolated environment: {str(e)}")
    
    def cleanup_environment(self, temp_base_dir: str):
        """Clean up isolated environment"""
        try:
            if not temp_base_dir or not os.path.exists(temp_base_dir):
                return
            
            logger.info(f"🧹 Cleaning up isolated environment: {temp_base_dir}")
            
            # Remove from tracking
            if temp_base_dir in self.active_environments:
                del self.active_environments[temp_base_dir]
            
            # Remove directory with retries (Windows can be stubborn)
            max_attempts = 3
            for attempt in range(max_attempts):
                try:
                    shutil.rmtree(temp_base_dir, ignore_errors=False)
                    logger.info("✅ Isolated environment cleaned up successfully")
                    break
                except OSError as e:
                    if attempt < max_attempts - 1:
                        logger.warning(f"⚠️ Cleanup attempt {attempt + 1} failed, retrying...")
                        time.sleep(1)
                    else:
                        logger.error(f"❌ Failed cleanup after {max_attempts} attempts: {e}")
                        # Schedule for cleanup on exit
                        import atexit
                        atexit.register(lambda: shutil.rmtree(temp_base_dir, ignore_errors=True))
                        
        except Exception as e:
            logger.error(f"❌ Error during cleanup: {e}")
    
    def get_active_environments(self) -> Dict[str, Dict]:
        """Get list of currently active environments"""
        return self.active_environments.copy()
    
    def cleanup_all_environments(self):
        """Clean up all active environments"""
        logger.info("🧹 Cleaning up all active environments...")
        for temp_dir in list(self.active_environments.keys()):
            self.cleanup_environment(temp_dir)

# Global environment manager
env_manager = None

def get_env_manager():
    """Get global environment manager instance"""
    global env_manager
    if env_manager is None:
        env_manager = VirtualEnvironmentManager()
    return env_manager