import re
import ast
import logging
from typing import List, Set, Any
from pathlib import Path

logger = logging.getLogger(__name__)

class DependencyParser:
    """Parses dependencies from downloaded tool files"""
    
    def __init__(self):
        # Common package name mappings
        self.package_mappings = {
            'cv2': 'opencv-python',
            'PIL': 'Pillow',
            'sklearn': 'scikit-learn',
            'yaml': 'PyYAML',
            'dotenv': 'python-dotenv'
        }
    
    def extract_dependencies_from_file(self, file_path: str) -> List[str]:
        """
        Extract dependencies from a tool file by parsing the dependencies variable
        
        Args:
            file_path: Path to the Python tool file
            
        Returns:
            List of unique package names to install
        """
        try:
            logger.info(f"📦 Extracting dependencies from: {file_path}")
            
            if not Path(file_path).exists():
                logger.error(f"❌ File not found: {file_path}")
                return []
            
            # Read the file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find dependencies variable in multiple ways
            dependencies_raw = self._find_dependencies_variable(content)
            
            if dependencies_raw is None:
                logger.info("ℹ️ No dependencies variable found in file")
                return []
            
            logger.info(f"🔍 Raw dependencies found: {dependencies_raw}")
            
            # Parse the dependencies
            clean_dependencies = self._parse_dependencies(dependencies_raw)
            
            logger.info(f"✅ Extracted {len(clean_dependencies)} unique dependencies: {clean_dependencies}")
            
            return clean_dependencies
            
        except Exception as e:
            logger.error(f"❌ Error extracting dependencies: {e}")
            return []
    
    def _find_dependencies_variable(self, content: str) -> Any:
        """Find dependencies variable in file content"""
        
        # Method 1: Look for dependencies = [...] pattern
        patterns = [
            r'dependencies\s*=\s*(\[.*?\])',  # dependencies = [...]
            r'dependencies\s*:\s*List.*?=\s*(\[.*?\])',  # dependencies: List = [...]
            r'dependencies\s*=\s*(\(.*?\))',  # dependencies = (...)
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.DOTALL | re.MULTILINE)
            if matches:
                try:
                    # Try to safely evaluate the first match
                    deps_str = matches[0].strip()
                    logger.info(f"🔍 Found dependencies pattern: {deps_str[:100]}...")
                    
                    # Use ast.literal_eval for safe evaluation
                    dependencies = ast.literal_eval(deps_str)
                    return dependencies
                except (ValueError, SyntaxError) as e:
                    logger.warning(f"⚠️ Could not parse dependencies with ast: {e}")
                    # Try manual parsing as fallback
                    return self._manual_parse_dependencies(deps_str)
        
        # Method 2: Look for class attribute
        class_pattern = r'class\s+\w+.*?dependencies\s*=\s*(\[.*?\])'
        matches = re.findall(class_pattern, content, re.DOTALL)
        if matches:
            try:
                deps_str = matches[0].strip()
                return ast.literal_eval(deps_str)
            except (ValueError, SyntaxError):
                return self._manual_parse_dependencies(deps_str)
        
        return None
    
    def _manual_parse_dependencies(self, deps_str: str) -> List:
        """Manual parsing for complex dependency formats"""
        try:
            # Clean up the string
            deps_str = deps_str.strip('[]()').strip()
            
            if not deps_str:
                return []
            
            # Split by commas but be careful of nested structures
            dependencies = []
            current_item = ""
            paren_count = 0
            bracket_count = 0
            in_quotes = False
            quote_char = None
            
            for char in deps_str:
                if char in ['"', "'"] and not in_quotes:
                    in_quotes = True
                    quote_char = char
                    current_item += char
                elif char == quote_char and in_quotes:
                    in_quotes = False
                    quote_char = None
                    current_item += char
                elif not in_quotes:
                    if char == '(':
                        paren_count += 1
                        current_item += char
                    elif char == ')':
                        paren_count -= 1
                        current_item += char
                    elif char == '[':
                        bracket_count += 1
                        current_item += char
                    elif char == ']':
                        bracket_count -= 1
                        current_item += char
                    elif char == ',' and paren_count == 0 and bracket_count == 0:
                        # End of current item
                        if current_item.strip():
                            dependencies.append(current_item.strip())
                        current_item = ""
                    else:
                        current_item += char
                else:
                    current_item += char
            
            # Add the last item
            if current_item.strip():
                dependencies.append(current_item.strip())
            
            logger.info(f"🔧 Manual parsing result: {dependencies}")
            return dependencies
            
        except Exception as e:
            logger.error(f"❌ Manual parsing failed: {e}")
            return []
    
    def _parse_dependencies(self, dependencies_raw: Any) -> List[str]:
        """Parse dependencies from various formats to clean package names"""
        
        if not dependencies_raw:
            return []
        
        logger.info(f"🔧 Parsing dependencies: {type(dependencies_raw)} = {dependencies_raw}")
        
        unique_packages = set()
        
        # Handle different input types
        if isinstance(dependencies_raw, str):
            # Single string dependency
            package = self._clean_package_name(dependencies_raw)
            if package:
                unique_packages.add(package)
                
        elif isinstance(dependencies_raw, (list, tuple)):
            # Process each item in the list/tuple
            for item in dependencies_raw:
                packages = self._process_dependency_item(item)
                unique_packages.update(packages)
        
        # Filter out empty strings and None values
        clean_packages = [pkg for pkg in unique_packages if pkg and pkg.strip()]
        
        return sorted(list(clean_packages))
    
    def _process_dependency_item(self, item: Any) -> Set[str]:
        """Process a single dependency item (could be string, tuple, list)"""
        
        packages = set()
        
        if isinstance(item, str):
            # Simple string: "pandas" or ""
            package = self._clean_package_name(item)
            if package:
                packages.add(package)
                
        elif isinstance(item, (tuple, list)):
            # Tuple/List: ("pandas", "pandas") or ["pandas", "pandas"]
            for sub_item in item:
                if isinstance(sub_item, str):
                    package = self._clean_package_name(sub_item)
                    if package:
                        packages.add(package)
                        
        else:
            # Try to convert to string
            try:
                item_str = str(item).strip()
                if item_str and item_str != 'None':
                    package = self._clean_package_name(item_str)
                    if package:
                        packages.add(package)
            except:
                pass
        
        return packages
    
    def _clean_package_name(self, package_name: str) -> str:
        """Clean and normalize package name"""
        
        if not package_name or not isinstance(package_name, str):
            return ""
        
        # Remove quotes and whitespace
        package = package_name.strip().strip('\'"').strip()
        
        # Skip empty strings
        if not package:
            return ""
        
        # Remove version specifiers (>=, ==, etc.)
        package = re.sub(r'[><=!]+.*$', '', package).strip()
        
        # Handle package mappings
        if package in self.package_mappings:
            package = self.package_mappings[package]
        
        # Validate package name format
        if re.match(r'^[a-zA-Z0-9][a-zA-Z0-9\-_.]*$', package):
            return package
        
        logger.warning(f"⚠️ Invalid package name format: '{package}'")
        return ""

# Global parser instance
parser = None

def get_parser():
    """Get global parser instance"""
    global parser
    if parser is None:
        parser = DependencyParser()
    return parser