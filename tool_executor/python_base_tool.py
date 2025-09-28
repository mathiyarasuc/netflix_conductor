import os
import importlib
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List, Optional, Tuple
import subprocess
import sys
import site
from pathlib import Path

logging.basicConfig(level=logging.INFO)


class MissingEnvironmentVariableError(Exception):
    pass


class DependencyNotInstalledError(Exception):
    pass


class InvalidSchemaError(Exception):
    pass


class CustomTypeError(TypeError):
    def __init__(self, message: str):  # Fixed: was _init_
        message = f"The tool only accepts input data as a dictionary.Any params the tool accepts should be keys in the input_data dictionary {message}"
        super().__init__(message)  # Fixed: was _init_


# tool_py_base_class
class BaseTool:
    """
    Base class for all tools in the platform.
    Handles validation, async execution, and dependency management.
    """

    name: str = "BaseTool"
    description: str = "Base class for all tools in the platform"
    version: str = "1.0"
    requires_env_vars: List[str] = []
    dependencies: List[Tuple[str, str]] = []
    uses_llm: bool = False
    default_llm_model: Optional[str] = None
    default_system_instructions: Optional[str] = None
    structured_output: bool = False
    input_schema: Dict[str, Any] = {}
    output_schema: Dict[str, Any] = {}
    config: Dict[str, Any] = {}
    direct_to_user: bool = False
    respond_back_to_agent: bool = False
    response_type: str = "filesystem"
    call_back_url: Optional[str] = None
    database_config_uri: Optional[str] = None

    def __init__(self, config: Optional[Dict[str, Any]] = None):  # Fixed: was _init_
        """Performs validation and ensures the tool is correctly configured."""
        if config:
            self.config = config.get("config", config)
        self._set_env_vars()
        self._validate_env_vars()
        self._validate_dependencies()
        self._validate_schemas()
        self._validate_llm_settings()

    def _set_env_vars(self):
        """Sets required environment variables from requires_env_vars."""
        for var in self.requires_env_vars:
            if ":" in var:
                env_var_name, env_var_value = var.split(":", 1)
                env_var_name = env_var_name.strip()
                env_var_value = env_var_value.strip()

                if not os.getenv(env_var_name):
                    os.environ[env_var_name] = env_var_value
                    logging.info(f"✅ Set environment variable: {env_var_name}")

    def _validate_env_vars(self):
        """Ensure all required environment variables are set."""
        missing_vars = []

        for var in self.requires_env_vars:
            env_var_name = var.split(":")[
                0
            ].strip()  # Extract the variable name before ':'

            if not os.getenv(env_var_name):  # Check if the variable is not set
                missing_vars.append(env_var_name)

        if missing_vars:
            raise MissingEnvironmentVariableError(
                f"Missing required environment variables: {missing_vars}"
            )

    def _validate_dependencies(self):
        """Skip dependency validation in isolated environment - handled externally"""
        # In isolated environment, dependencies are installed separately
        # This method is disabled to avoid conflicts
        logging.info("📦 Dependency validation skipped - handled by isolation system")
        pass

    def _validate_schemas(self):
        """Ensure input and output schemas are properly formatted."""
        if not isinstance(self.input_schema, dict) or not isinstance(
            self.output_schema, dict
        ):
            raise InvalidSchemaError(
                "Input and output schemas must be valid dictionaries."
            )

    def _validate_llm_settings(self):
        """Ensure LLM-related settings are valid if uses_llm is enabled."""
        if self.uses_llm:
            if not self.default_llm_model:
                raise ValueError(
                    "LLM usage is enabled, but no default LLM model is set."
                )
            if not isinstance(self.default_system_instructions, (str, type(None))):
                raise ValueError("System instructions must be a string or None.")

    def run_sync(self, *args, **kwargs) -> Dict[str, Any]:
        raise NotImplementedError("Subclasses must implement the 'run_sync' method.")

    async def run_async(
        self, input_data: Dict[str, Any], llm_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Asynchronous execution method. Optional but falls back to run_sync."""
        loop = asyncio.get_running_loop()
        with ThreadPoolExecutor() as pool:
            return await loop.run_in_executor(
                pool, self.run_sync, input_data, llm_config
            )