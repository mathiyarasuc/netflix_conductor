import re
import json
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

logger = logging.getLogger(__name__)

class SchemaValidator:
    """Validates user input against tool input schemas"""
    
    def __init__(self):
        self.type_converters = {
            'string': self._convert_to_string,
            'integer': self._convert_to_integer,
            'number': self._convert_to_number,
            'boolean': self._convert_to_boolean,
            'array': self._convert_to_array,
            'object': self._convert_to_object
        }
    
    def _normalize_schema(self, input_schema: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize schemas that have wrapper objects without type declarations"""
        
        properties = input_schema.get("properties", {})
        
        # Check for wrapper pattern: single property containing nested fields
        if len(properties) == 1:
            wrapper_key = list(properties.keys())[0]
            wrapper_value = properties[wrapper_key]
            
            # If wrapper contains fields that look like schema properties but no type
            if (isinstance(wrapper_value, dict) and 
                not wrapper_value.get("type") and
                any(isinstance(v, dict) and v.get("type") for v in wrapper_value.values())):
                
                logger.info(f"🔧 Detected wrapper pattern: {wrapper_key}")
                
                # Create normalized schema
                return {
                    "type": "object",
                    "properties": wrapper_value,
                    "required": input_schema.get("required", []),
                    "_wrapper_key": wrapper_key
                }
        
        return input_schema
    
    def validate_input(self, user_input: Dict[str, Any], input_schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate user input against tool's input schema - HANDLES WRAPPER PATTERNS
        """
        try:
            logger.info("🔍 Starting ADVANCED input validation...")
            
            # Normalize schema to handle wrapper patterns
            normalized_schema = self._normalize_schema(input_schema)
            wrapper_key = normalized_schema.get("_wrapper_key")
            
            if wrapper_key:
                logger.info(f"🔄 Unwrapping input data from: {wrapper_key}")
                # If input is wrapped, unwrap it for validation
                if wrapper_key in user_input:
                    validation_data = user_input[wrapper_key]
                else:
                    validation_data = user_input
            else:
                validation_data = user_input
            
            logger.info(f"📝 Validation data: {validation_data}")
            logger.info(f"📋 Normalized schema: {normalized_schema}")
            
            if not normalized_schema.get("properties"):
                return {
                    "valid": True,
                    "data": user_input,
                    "errors": [],
                    "warnings": ["No properties to validate"]
                }
            
            # Perform recursive validation
            validation_result = self._validate_object_recursive(
                validation_data, 
                normalized_schema, 
                "root"
            )
            
            # Reconstruct wrapper if needed
            if wrapper_key and validation_result["valid"]:
                validation_result["data"] = {wrapper_key: validation_result["data"]}
            
            return validation_result
            
        except Exception as e:
            logger.error(f"❌ Error during advanced validation: {e}")
            return {
                "valid": False,
                "data": {},
                "errors": [f"Validation error: {str(e)}"],
                "warnings": []
            }

    def _validate_object_recursive(self, data: Dict[str, Any], schema: Dict[str, Any], path: str) -> Dict[str, Any]:
        """RECURSIVE validation for nested objects"""
        
        properties = schema.get("properties", {})
        required_fields = schema.get("required", [])
        
        validation_result = {
            "valid": True,
            "data": {},
            "errors": [],
            "warnings": []
        }
        
        # Check required fields
        for field in required_fields:
            if field not in data:
                validation_result["errors"].append(f"Missing required field: '{path}.{field}' if path != 'root' else field")
                validation_result["valid"] = False
        
        # Validate each field recursively
        for field_name, field_value in data.items():
            if field_name not in properties:
                validation_result["warnings"].append(f"Unknown field '{path}.{field_name}' - will be passed through")
                validation_result["data"][field_name] = field_value
                continue
            
            field_schema = properties[field_name]
            field_path = f"{path}.{field_name}" if path != "root" else field_name
            field_result = self._validate_field_recursive(field_name, field_value, field_schema, field_path)
            
            if field_result["valid"]:
                validation_result["data"][field_name] = field_result["value"]
                if field_result.get("warnings"):
                    validation_result["warnings"].extend(field_result["warnings"])
            else:
                validation_result["errors"].extend(field_result["errors"])
                validation_result["valid"] = False
        
        # Apply default values for missing optional fields
        for field_name, field_schema in properties.items():
            if field_name not in validation_result["data"] and "default" in field_schema:
                default_value = field_schema["default"]
                validation_result["data"][field_name] = default_value
                validation_result["warnings"].append(f"Applied default value for '{field_path}': {default_value}")
        
        return validation_result

    def _validate_field_recursive(self, field_name: str, value: Any, field_schema: Dict[str, Any], field_path: str) -> Dict[str, Any]:
            """RECURSIVE field validation for nested structures - WITH UNION TYPE SUPPORT"""
            
            result = {
                "valid": True,
                "value": value,
                "errors": [],
                "warnings": []
            }
            
            try:
                field_type = field_schema.get("type", "string")
                
                # 🔧 HANDLE UNION TYPES (e.g., ['integer', 'string'])
                if isinstance(field_type, list):
                    logger.info(f"🔄 Processing union type {field_type} for field '{field_name}'")
                    conversion_successful = False
                    conversion_errors = []
                    
                    # Try each type in the union until one works
                    for union_type in field_type:
                        try:
                            if value is not None:
                                converted_value = self._convert_type(value, union_type)
                                result["value"] = converted_value
                                logger.info(f"✅ Successfully converted '{field_name}' to {union_type}: {converted_value}")
                            
                            # Validate constraints for this specific type
                            temp_schema = {**field_schema, "type": union_type}
                            self._validate_constraints(field_name, result["value"], temp_schema, result)
                            
                            if result["valid"]:
                                conversion_successful = True
                                result["warnings"].append(f"Field '{field_name}' validated as {union_type}")
                                break  # Success, stop trying other types
                            else:
                                # Constraints failed, try next type
                                conversion_errors.append(f"Type {union_type} failed constraints: {result['errors']}")
                                result["errors"] = []  # Reset errors for next attempt
                                result["valid"] = True  # Reset valid flag
                                
                        except (ValueError, TypeError) as e:
                            conversion_errors.append(f"Cannot convert to {union_type}: {str(e)}")
                            continue  # Try next type in union
                    
                    if not conversion_successful:
                        # None of the union types worked
                        result["valid"] = False
                        result["errors"].append(f"Field '{field_name}': Value '{value}' doesn't match any allowed types {field_type}. Errors: {conversion_errors}")
                    
                    return result
                
                # Single type handling (existing logic)
                elif field_type == "object" and isinstance(value, dict):
                    # NESTED OBJECT - validate recursively
                    nested_result = self._validate_object_recursive(value, field_schema, field_path)
                    result["value"] = nested_result["data"]
                    result["valid"] = nested_result["valid"]
                    result["errors"] = nested_result["errors"]
                    result["warnings"] = nested_result["warnings"]
                    
                elif field_type == "array" and isinstance(value, list):
                    # ARRAY - validate each item
                    if field_schema.get("items", {}).get("type") == "object":
                        # Array of objects
                        validated_items = []
                        for i, item in enumerate(value):
                            item_result = self._validate_object_recursive(item, field_schema["items"], f"{field_path}[{i}]")
                            if item_result["valid"]:
                                validated_items.append(item_result["data"])
                                result["warnings"].extend(item_result["warnings"])
                            else:
                                result["errors"].extend(item_result["errors"])
                                result["valid"] = False
                        
                        if result["valid"]:
                            result["value"] = validated_items
                    else:
                        # Simple array - existing logic
                        result["value"] = value
                        
                else:
                    # SIMPLE FIELD - existing validation logic
                    if value is not None:
                        converted_value = self._convert_type(value, field_type)
                        result["value"] = converted_value
                    
                    # Validate constraints
                    self._validate_constraints(field_name, result["value"], field_schema, result)
                
            except Exception as e:
                result["valid"] = False
                result["errors"].append(f"Field '{field_path}': {str(e)}")
            
            return result
    
    def _validate_field(self, field_name: str, value: Any, field_schema: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a single field against its schema"""
        
        result = {
            "valid": True,
            "value": value,
            "errors": [],
            "warnings": []
        }
        
        try:
            # Get field type
            field_type = field_schema.get("type", "string")
            
            # Convert value to correct type
            if value is not None:
                converted_value = self._convert_type(value, field_type)
                result["value"] = converted_value
            
            # Validate constraints
            self._validate_constraints(field_name, result["value"], field_schema, result)
            
        except Exception as e:
            result["valid"] = False
            result["errors"].append(f"Field '{field_name}': {str(e)}")
        
        return result
    
    def _convert_type(self, value: Any, target_type: str) -> Any:
        """Convert value to target type"""
        
        if value is None:
            return None
        
        converter = self.type_converters.get(target_type, self._convert_to_string)
        return converter(value)
    
    def _convert_to_string(self, value: Any) -> str:
        """Convert value to string"""
        if isinstance(value, str):
            return value
        return str(value)
    
    def _convert_to_integer(self, value: Any) -> int:
        """Convert value to integer"""
        if isinstance(value, int):
            return value
        if isinstance(value, float):
            return int(value)
        if isinstance(value, str):
            if value.strip().isdigit():
                return int(value.strip())
            # Handle negative numbers
            if value.strip().lstrip('-').isdigit():
                return int(value.strip())
        raise ValueError(f"Cannot convert '{value}' to integer")
    
    def _convert_to_number(self, value: Any) -> Union[int, float]:
        """Convert value to number (int or float)"""
        if isinstance(value, (int, float)):
            return value
        if isinstance(value, str):
            try:
                # Try integer first
                if '.' not in value and 'e' not in value.lower():
                    return int(value)
                else:
                    return float(value)
            except ValueError:
                pass
        raise ValueError(f"Cannot convert '{value}' to number")
    
    def _convert_to_boolean(self, value: Any) -> bool:
        """Convert value to boolean"""
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            lower_val = value.lower().strip()
            if lower_val in ['true', '1', 'yes', 'on']:
                return True
            elif lower_val in ['false', '0', 'no', 'off']:
                return False
        if isinstance(value, int):
            return bool(value)
        raise ValueError(f"Cannot convert '{value}' to boolean")
    
    def _convert_to_array(self, value: Any) -> List[Any]:
        """Convert value to array/list"""
        if isinstance(value, list):
            return value
        if isinstance(value, tuple):
            return list(value)
        if isinstance(value, str):
            # Try to parse JSON array
            try:
                parsed = json.loads(value)
                if isinstance(parsed, list):
                    return parsed
            except json.JSONDecodeError:
                pass
            # Split by comma as fallback
            return [item.strip() for item in value.split(',') if item.strip()]
        raise ValueError(f"Cannot convert '{value}' to array")
    
    def _convert_to_object(self, value: Any) -> Dict[str, Any]:
        """Convert value to object/dict"""
        if isinstance(value, dict):
            return value
        if isinstance(value, str):
            try:
                parsed = json.loads(value)
                if isinstance(parsed, dict):
                    return parsed
            except json.JSONDecodeError:
                pass
        raise ValueError(f"Cannot convert '{value}' to object")
    
    def _validate_constraints(self, field_name: str, value: Any, field_schema: Dict[str, Any], result: Dict[str, Any]):
        """Validate field constraints (enum, pattern, min/max, etc.)"""
        
        if value is None:
            return
        
        # Enum validation
        if "enum" in field_schema:
            allowed_values = field_schema["enum"]
            if value not in allowed_values:
                result["errors"].append(f"Field '{field_name}' must be one of: {allowed_values}, got: {value}")
                result["valid"] = False
        
        # Pattern validation (for strings)
        if "pattern" in field_schema and isinstance(value, str):
            pattern = field_schema["pattern"]
            if not re.match(pattern, value):
                result["errors"].append(f"Field '{field_name}' must match pattern: {pattern}")
                result["valid"] = False
        
        # Numeric constraints
        if isinstance(value, (int, float)):
            if "minimum" in field_schema and value < field_schema["minimum"]:
                result["errors"].append(f"Field '{field_name}' must be >= {field_schema['minimum']}")
                result["valid"] = False
            
            if "maximum" in field_schema and value > field_schema["maximum"]:
                result["errors"].append(f"Field '{field_name}' must be <= {field_schema['maximum']}")
                result["valid"] = False
        
        # String length constraints
        if isinstance(value, str):
            if "minLength" in field_schema and len(value) < field_schema["minLength"]:
                result["errors"].append(f"Field '{field_name}' must be at least {field_schema['minLength']} characters")
                result["valid"] = False
            
            if "maxLength" in field_schema and len(value) > field_schema["maxLength"]:
                result["errors"].append(f"Field '{field_name}' must be at most {field_schema['maxLength']} characters")
                result["valid"] = False
        
        # Array constraints
        if isinstance(value, list):
            if "minItems" in field_schema and len(value) < field_schema["minItems"]:
                result["errors"].append(f"Field '{field_name}' must have at least {field_schema['minItems']} items")
                result["valid"] = False
            
            if "maxItems" in field_schema and len(value) > field_schema["maxItems"]:
                result["errors"].append(f"Field '{field_name}' must have at most {field_schema['maxItems']} items")
                result["valid"] = False

# Global validator instance
validator = None

def get_validator():
    """Get global validator instance"""
    global validator
    if validator is None:
        validator = SchemaValidator()
    return validator
