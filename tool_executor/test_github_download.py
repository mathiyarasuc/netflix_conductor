"""
Test script to verify GitHub download functionality using GitHub API
"""
from github_downloader import get_downloader
from virtual_env_manager import get_env_manager
import logging
import tempfile

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_github_download():
    """Test downloading a real tool from GitHub using API"""
    try:
        logger.info("🚀 Testing GitHub tool download using API...")
        
        # Test with a known tool from the repository
        test_tool_name = "NAICSExcelTool"
        logger.info(f"🎯 Testing with tool: {test_tool_name}")
        
        # Create temporary directory for test
        with tempfile.TemporaryDirectory() as temp_dir:
            logger.info(f"📁 Test directory: {temp_dir}")
            
            # Download the tool using GitHub API
            downloader = get_downloader()
            result = downloader.download_tool_from_github(
                tool_name=test_tool_name,
                target_dir=temp_dir
            )
            
            if result["status"] != "success":
                logger.error(f"❌ Download failed: {result.get('message')}")
                return False
            
            # Verify the file
            file_path = result["file_path"]
            verification = downloader.verify_tool_file(file_path)
            
            logger.info("📊 Download Results:")
            logger.info(f"   File size: {result['file_size']} bytes")
            logger.info(f"   File path: {result['file_path']}")
            
            logger.info("📊 Verification Results:")
            for key, value in verification.items():
                logger.info(f"   {key}: {value}")
            
            if verification["valid"]:
                logger.info("🎉 GitHub API download test completed successfully!")
                return True
            else:
                logger.error("❌ Downloaded file failed verification")
                return False
                
    except Exception as e:
        logger.error(f"❌ GitHub API download test failed: {e}")
        return False

def test_list_tools():
    """Test listing available tools from GitHub"""
    try:
        logger.info("🚀 Testing tool listing from GitHub...")
        
        downloader = get_downloader()
        tools = downloader.list_available_tools()
        
        if tools:
            logger.info(f"✅ Found {len(tools)} tools in repository")
            return True
        else:
            logger.error("❌ No tools found")
            return False
            
    except Exception as e:
        logger.error(f"❌ Tool listing test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing GitHub API Integration...")
    
    # Test 1: List available tools
    success1 = test_list_tools()
    
    # Test 2: Download a specific tool
    success2 = test_github_download()
    
    if success1 and success2:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")