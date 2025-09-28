"""
Test script to verify dependency parsing functionality
"""
from dependency_parser import get_parser
from github_downloader import get_downloader
import logging
import tempfile

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_dependency_parsing():
    """Test parsing dependencies from a real downloaded tool"""
    try:
        logger.info("🚀 Testing dependency parsing...")
        
        # Download a tool that has dependencies
        downloader = get_downloader()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Download NAICSExcelTool (has dependencies)
            result = downloader.download_tool_from_github("NAICSExcelTool", temp_dir)
            
            if result["status"] != "success":
                logger.error(f"❌ Failed to download tool: {result.get('message')}")
                return False
            
            # Parse dependencies
            parser = get_parser()
            dependencies = parser.extract_dependencies_from_file(result["file_path"])
            
            logger.info("📊 Dependency Parsing Results:")
            logger.info(f"   Tool: NAICSExcelTool")
            logger.info(f"   Dependencies found: {len(dependencies)}")
            for i, dep in enumerate(dependencies, 1):
                logger.info(f"   {i}. {dep}")
            
            # Test with different tools
            test_tools = ["ClaimsIntelSearch", "SOVDataFetcher"]
            
            for tool_name in test_tools:
                try:
                    logger.info(f"🔧 Testing {tool_name}...")
                    result = downloader.download_tool_from_github(tool_name, temp_dir)
                    
                    if result["status"] == "success":
                        deps = parser.extract_dependencies_from_file(result["file_path"])
                        logger.info(f"   {tool_name}: {len(deps)} dependencies - {deps}")
                    else:
                        logger.warning(f"   {tool_name}: Download failed")
                        
                except Exception as e:
                    logger.warning(f"   {tool_name}: Error - {e}")
            
            logger.info("🎉 Dependency parsing test completed!")
            return True
            
    except Exception as e:
        logger.error(f"❌ Dependency parsing test failed: {e}")
        return False

def test_parsing_formats():
    """Test parsing different dependency formats manually"""
    try:
        logger.info("🚀 Testing different dependency formats...")
        
        parser = get_parser()
        
        # Test cases from your examples
        test_cases = [
            # Format 1: Tuples
            [("pandas", "pandas"), ("openpyxl", "openpyxl")],
            
            # Format 2: Mixed with empty strings
            [["pandas", "pandas"], ["openpyxl", "openpyxl"], ""],
            
            # Format 3: Simple list
            ["pandas", "numpy", "requests"],
            
            # Format 4: Empty
            [],
            
            # Format 5: Single tuple
            ("pymongo", "pymongo"),
            
            # Format 6: With empty items
            ["pandas", "", "numpy", None]
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            logger.info(f"🧪 Test case {i}: {test_case}")
            result = parser._parse_dependencies(test_case)
            logger.info(f"   Result: {result}")
            logger.info("")
        
        logger.info("🎉 Format parsing test completed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Format parsing test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Dependency Parser...")
    
    # Test 1: Parse real tool dependencies
    success1 = test_dependency_parsing()
    
    # Test 2: Test different formats
    success2 = test_parsing_formats()
    
    if success1 and success2:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")