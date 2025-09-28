"""
Test script to verify virtual environment creation works
"""
from virtual_env_manager import get_env_manager
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_virtual_environment():
    """Test creating and cleaning up virtual environment"""
    env_manager = get_env_manager()
    
    try:
        logger.info("🚀 Testing virtual environment creation...")
        
        # Test environment creation
        env_info = env_manager.create_isolated_environment("test_tool")
        
        logger.info("📊 Environment Info:")
        for key, value in env_info.items():
            logger.info(f"   {key}: {value}")
        
        # Test cleanup
        logger.info("🧹 Testing cleanup...")
        env_manager.cleanup_environment(env_info["temp_base_dir"])
        
        logger.info("🎉 Virtual environment test completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Virtual environment test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_virtual_environment()
    if success:
        print("✅ All tests passed!")
    else:
        print("❌ Tests failed!")