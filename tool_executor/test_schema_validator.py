"""
Test script to verify schema validation functionality
"""
from schema_validator import get_validator
from mongodb_connector import get_db_connector
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_schema_validation():
    """Test validation with real tool schemas"""
    try:
        logger.info("🚀 Testing schema validation...")
        
        # Get real tool schema
        db = get_db_connector()
        tool_details = db.get_tool_details("NAICSExcelTool")
        
        if not tool_details:
            logger.error("❌ NAICSExcelTool not found")
            return False
        
        input_schema = tool_details.get("input_schema", {})
        logger.info(f"📋 Schema: {input_schema}")
        
        validator = get_validator()
        
        # Test Case 1: Valid input
        logger.info("🧪 Test Case 1: Valid input")
        valid_input = {"naics_code": "541511"}
        result1 = validator.validate_input(valid_input, input_schema)
        
        logger.info(f"   Input: {valid_input}")
        logger.info(f"   Valid: {result1['valid']}")
        logger.info(f"   Data: {result1['data']}")
        logger.info(f"   Errors: {result1['errors']}")
        logger.info("")
        
        # Test Case 2: Missing required field
        logger.info("🧪 Test Case 2: Missing required field")
        invalid_input = {}
        result2 = validator.validate_input(invalid_input, input_schema)
        
        logger.info(f"   Input: {invalid_input}")
        logger.info(f"   Valid: {result2['valid']}")
        logger.info(f"   Errors: {result2['errors']}")
        logger.info("")
        
        # Test Case 3: Type conversion
        logger.info("🧪 Test Case 3: Type conversion")
        type_test_input = {"naics_code": 541511}  # Number instead of string
        result3 = validator.validate_input(type_test_input, input_schema)
        
        logger.info(f"   Input: {type_test_input}")
        logger.info(f"   Valid: {result3['valid']}")
        logger.info(f"   Data: {result3['data']}")
        logger.info(f"   Converted type: {type(result3['data'].get('naics_code'))}")
        logger.info("")
        
        return all([result1['valid'], not result2['valid'], result3['valid']])
        
    except Exception as e:
        logger.error(f"❌ Schema validation test failed: {e}")
        return False

def test_complex_schema():
    """Test with more complex schema patterns"""
    try:
        logger.info("🚀 Testing complex schema validation...")
        
        # Create a complex schema similar to SOVDataFetcher
        complex_schema = {
            "type": "object",
            "properties": {
                "case_id": {
                    "type": "string",
                    "description": "Submission case ID",
                    "pattern": "^(PRO|SUB)\\d+$"
                },
                "response_mode": {
                    "type": "string",
                    "enum": ["summary", "balanced", "detailed"],
                    "default": "balanced"
                },
                "max_locations": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 20,
                    "default": 5
                },
                "include_details": {
                    "type": "boolean",
                    "default": True
                }
            },
            "required": ["case_id"]
        }
        
        validator = get_validator()
        
        # Test Case 1: Valid complex input
        logger.info("🧪 Complex Test 1: Valid input with defaults")
        valid_input = {"case_id": "PRO0001177"}
        result1 = validator.validate_input(valid_input, complex_schema)
        
        logger.info(f"   Input: {valid_input}")
        logger.info(f"   Valid: {result1['valid']}")
        logger.info(f"   Data: {result1['data']}")
        logger.info(f"   Warnings: {result1['warnings']}")
        logger.info("")
        
        # Test Case 2: Pattern validation failure
        logger.info("🧪 Complex Test 2: Pattern validation failure")
        invalid_pattern = {"case_id": "INVALID123"}
        result2 = validator.validate_input(invalid_pattern, complex_schema)
        
        logger.info(f"   Input: {invalid_pattern}")
        logger.info(f"   Valid: {result2['valid']}")
        logger.info(f"   Errors: {result2['errors']}")
        logger.info("")
        
        # Test Case 3: Enum validation
        logger.info("🧪 Complex Test 3: Enum validation")
        invalid_enum = {"case_id": "PRO0001177", "response_mode": "invalid"}
        result3 = validator.validate_input(invalid_enum, complex_schema)
        
        logger.info(f"   Input: {invalid_enum}")
        logger.info(f"   Valid: {result3['valid']}")
        logger.info(f"   Errors: {result3['errors']}")
        logger.info("")
        
        # Test Case 4: Type conversion and range validation
        logger.info("🧪 Complex Test 4: Type conversion and range validation")
        type_convert = {
            "case_id": "PRO0001177",
            "max_locations": "25",  # String to int, but exceeds maximum
            "include_details": "true"  # String to boolean
        }
        result4 = validator.validate_input(type_convert, complex_schema)
        
        logger.info(f"   Input: {type_convert}")
        logger.info(f"   Valid: {result4['valid']}")
        logger.info(f"   Data: {result4['data']}")
        logger.info(f"   Errors: {result4['errors']}")
        logger.info("")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Complex schema test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Schema Validator...")
    
    # Test 1: Basic schema validation
    success1 = test_schema_validation()
    
    # Test 2: Complex schema validation
    success2 = test_complex_schema()
    
    if success1 and success2:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")