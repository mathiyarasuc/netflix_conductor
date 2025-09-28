import os
from dotenv import load_dotenv
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
import time
from github import Github

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class GitHubToolDownloader:
    """Downloads tools from GitHub repository using GitHub API"""
    
    def __init__(self):
        # Get token from environment variable
        self.BACKEND_VARIABLE = os.getenv('GITHUB_TOKEN')
        if not self.BACKEND_VARIABLE:
            raise ValueError("GITHUB_TOKEN environment variable is required")
        self.main_repo_owner = "vsrin"
        self.main_repo_name = "Tool_Chest"
        self.tools_folder = "Tools"
        self.github_client = None
        self.repo = None
        
    def _connect_to_github(self):
        """Connect to GitHub repository"""
        if not self.github_client:
            logger.info("🌐 Connecting to GitHub repository...")
            self.github_client = Github(self.BACKEND_VARIABLE)
            self.repo = self.github_client.get_repo(f"{self.main_repo_owner}/{self.main_repo_name}")
            logger.info(f"📁 Connected to repository: {self.main_repo_owner}/{self.main_repo_name}")
    
    def download_tool_from_github(self, tool_name: str, target_dir: str) -> Dict[str, Any]:
        """
        Download a tool from GitHub repository using your existing pattern
        
        Args:
            tool_name: Name of the tool (e.g., "NAICSExcelTool")
            target_dir: Directory to save the tool file (isolated environment tools_dir)
            
        Returns:
            Dict with download status and file path
        """
        try:
            logger.info(f"🔧 DOWNLOADING TOOL FROM GITHUB: {tool_name}")
            logger.info("=" * 60)
            
            # Connect to GitHub
            self._connect_to_github()
            
            logger.info(f"🔍 Looking for: {self.tools_folder}/{tool_name}.py")
            
            # Ensure target directory exists
            target_path = Path(target_dir)
            target_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"📁 Target directory: {target_path}")
            
            try:
                # Fetch the tool content from GitHub (your exact pattern)
                tool_content = self.repo.get_contents(f"{self.tools_folder}/{tool_name}.py")
                tool_file_path = target_path / f"{tool_name}.py"
                
                # Save the tool file (your exact pattern)
                with tool_file_path.open("wb") as f:
                    f.write(tool_content.decoded_content)
                
                logger.info(f"✅ Successfully downloaded: {tool_name}")
                logger.info(f"💾 Saved to: {tool_file_path}")
                
                # Display file info (your exact pattern)
                file_size = tool_file_path.stat().st_size
                logger.info(f"📊 File size: {file_size} bytes")
                logger.info(f"📁 Full path: {tool_file_path.absolute()}")
                
                # Show code preview (your exact pattern)
                logger.info(f"🐍 Preview of {tool_name}.py:")
                logger.info("=" * 60)
                
                with tool_file_path.open("r", encoding='utf-8') as f:
                    lines = f.readlines()
                    preview_lines = min(10, len(lines))  # Shortened for logs
                    
                    for i, line in enumerate(lines[:preview_lines], 1):
                        logger.info(f"{i:2d}: {line.rstrip()}")
                    
                    if len(lines) > preview_lines:
                        logger.info(f"... and {len(lines) - preview_lines} more lines")
                
                logger.info("=" * 60)
                logger.info(f"✅ TOOL DOWNLOAD COMPLETED SUCCESSFULLY!")
                
                # Return success info
                return {
                    "status": "success",
                    "tool_name": tool_name,
                    "file_path": str(tool_file_path),
                    "file_size": file_size,
                    "filename": f"{tool_name}.py",
                    "download_time": time.time()
                }
                
            except Exception as e:
                if "404" in str(e):
                    error_msg = f"Tool '{tool_name}.py' not found in repository!"
                    logger.error(f"❌ {error_msg}")
                    logger.info(f"💡 Make sure the tool exists in: {self.main_repo_owner}/{self.main_repo_name}/{self.tools_folder}/")
                    
                    # Suggest similar tools from GitHub (your exact pattern)
                    try:
                        all_files = self.repo.get_contents(self.tools_folder)
                        available_tools = [f.name.replace('.py', '') for f in all_files if f.name.endswith('.py')]
                        
                        similar_tools = [t for t in available_tools if tool_name.lower() in t.lower() or t.lower() in tool_name.lower()]
                        
                        if similar_tools:
                            logger.info(f"💡 Did you mean one of these?")
                            for similar_tool in similar_tools[:5]:
                                logger.info(f"   • {similar_tool}")
                    except Exception:
                        pass
                    
                    return {"status": "error", "message": error_msg}
                else:
                    error_msg = f"Error downloading tool: {str(e)}"
                    logger.error(f"❌ {error_msg}")
                    return {"status": "error", "message": error_msg}
                    
        except Exception as e:
            error_msg = f"Error connecting to GitHub: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return {"status": "error", "message": error_msg}
    
    def list_available_tools(self) -> list:
        """List available tools from GitHub repository (your exact pattern)"""
        try:
            logger.info("📋 AVAILABLE TOOLS")
            logger.info("=" * 60)
            
            # Connect to GitHub
            self._connect_to_github()
            
            # Get tools from GitHub repository (your exact pattern)
            logger.info("🌐 Fetching from GitHub repository...")
            
            github_files = self.repo.get_contents(self.tools_folder)
            github_tools = [f.name.replace('.py', '') for f in github_files if f.name.endswith('.py')]
            
            logger.info(f"📁 Found {len(github_tools)} tools in GitHub repository:")
            logger.info("-" * 60)
            
            for i, tool_name in enumerate(github_tools, 1):
                logger.info(f"{i:2d}. {tool_name}")
            
            logger.info("-" * 60)
            
            return github_tools
            
        except Exception as e:
            logger.error(f"❌ Error listing tools: {str(e)}")
            return []
    
    def verify_tool_file(self, file_path: str) -> Dict[str, Any]:
        """
        Verify that downloaded file is a valid Python tool
        """
        try:
            logger.info(f"🔍 Verifying tool file: {file_path}")
            
            if not os.path.exists(file_path):
                return {"valid": False, "error": "File does not exist"}
            
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            verification_results = {
                "valid": True,
                "file_size": len(content),
                "has_class": "class " in content,
                "has_basetool": "BaseTool" in content,
                "has_run_sync": "def run_sync" in content,
                "has_input_schema": "input_schema" in content,
                "has_dependencies": "dependencies" in content,
                "errors": []
            }
            
            # Check for required elements
            if not verification_results["has_class"]:
                verification_results["errors"].append("No class definition found")
            
            if not verification_results["has_basetool"]:
                verification_results["errors"].append("No BaseTool inheritance found")
            
            if not verification_results["has_run_sync"]:
                verification_results["errors"].append("No run_sync method found")
            
            # Overall validity
            verification_results["valid"] = len(verification_results["errors"]) == 0
            
            if verification_results["valid"]:
                logger.info("✅ Tool file verification passed")
            else:
                logger.warning(f"⚠️ Tool file verification issues: {verification_results['errors']}")
            
            return verification_results
            
        except Exception as e:
            logger.error(f"❌ Error verifying tool file: {e}")
            return {"valid": False, "error": str(e)}

# Global downloader instance
downloader = None

def get_downloader():
    """Get global downloader instance"""
    global downloader
    if downloader is None:
        downloader = GitHubToolDownloader()

    return downloader

