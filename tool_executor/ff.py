#!/usr/bin/env python3

"""
=============================================================================
FETCH SUBMISSION DATA TOOL
=============================================================================

Standalone tool that fetches and processes submission data from Bold Penguin API.
Extracts the data fetching and parsing logic from the Conductor workflow worker into a 
reusable tool following Blueprint/Studio tool format.

FUNCTIONALITY:
- Fetches data from multiple Bold Penguin data packages
- Parses and structures response data using custom parsers
- Saves processed data to MongoDB collections
- Returns structured submission data

DESIGN PRINCIPLE: Retrieve and process submission data from Bold Penguin services with structured parsing.
"""

import os
import json
import logging
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime
from contextlib import contextmanager

# Blueprint compliance import
try:
    from python_base_tool import BaseTool
except ImportError:
    from tool_py_base_class import BaseTool

import requests
import pymongo
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, PyMongoError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FetchSubmissionDataTool(BaseTool):
    """
    Submission data fetching tool for Bold Penguin API operations.
    Retrieves, parses, and structures data from multiple data packages.
    """

    # ==========================================================================
    # STUDIO BLUEPRINT METADATA
    # ==========================================================================
    
    name = "FetchSubmissionDataTool"
    description = "Fetches and processes submission data from Bold Penguin API. Retrieves data from multiple data packages, applies custom parsing, and saves structured data to MongoDB."
    
    requires_env_vars = []
    dependencies = [("requests", "requests"), ("pymongo", "pymongo")]
    uses_llm = False
    default_llm_model = None
    default_system_instructions = None
    structured_output = True

    # ==========================================================================
    # STUDIO BLUEPRINT SCHEMAS
    # ==========================================================================
    
    input_schema = {
        "type": "object",
        "properties": {
            "auth_token": {
                "type": "string",
                "description": "Authentication token for API access"
            },
            "tx_id": {
                "type": "string",
                "description": "Transaction ID from processing"
            },
            "case_id": {
                "type": "string",
                "description": "Case ID for data organization"
            }
        },
        "required": ["auth_token", "tx_id", "case_id"],
        "additionalProperties": True
    }

    output_schema = {
        "type": "object",
        "properties": {
            "Common": {"type": "object"},
            "Loss Run": {"type": "object"},
            "Property": {"type": "array"},
            "Advanced Property": {"type": "array"},
            "General Liability": {"type": "object"},
            "Auto": {"type": "object"},
            "Workers Compensation": {"type": "object"}
        },
        "additionalProperties": True
    }

    # ==========================================================================
    # CONFIGURATION
    # ==========================================================================
    
    config = {
        "api_key": "LCLSzoQf8R3zPtj2ZvQR19JkLYtDHREV2jpgMH4g",
        "data_package_ids": [
            "elevate-us-common-c0001",
            "default-us-admitted-advanced-property-l0001",
            "default-us-loss-run-c0001",
            "elevate-us-gl-c0001",
            "elevate-us-property-l0001",
            "elevate-us-admitted-auto-c0001",
            "elevate-us-admitted-workers-comp-c0001"
        ],
        "mongo_uri": "mongodb+srv://artifi:root@artifi.2vi2m.mongodb.net/?retryWrites=true&w=majority&appName=Artifi",
        "database_name": "Submission_Intake"
    }
    
    direct_to_user = False
    respond_back_to_agent = True
    response_type = "json"
    call_back_url = None

    # ==========================================================================
    # INITIALIZATION
    # ==========================================================================

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize submission data fetching tool."""
        super().__init__(config)
        
        if config:
            self.config.update(config)
        
        logger.info("FetchSubmissionDataTool initialized")

    @contextmanager
    def _get_database_connection(self):
        """Context manager for MongoDB connection with guaranteed cleanup."""
        client = None
        try:
            client = MongoClient(self.config["mongo_uri"])
            client.admin.command('ping')
            db = client[self.config["database_name"]]
            yield db
        except Exception as e:
            logger.error(f"Database operation error: {str(e)}")
            raise
        finally:
            if client:
                try:
                    client.close()
                except Exception as cleanup_error:
                    logger.warning(f"Warning during connection cleanup: {str(cleanup_error)}")

    # ==========================================================================
    # PARSER METHODS (COPIED FROM CODEBASE)
    # ==========================================================================

    def parse_us_common(self, json_data):
        data = json_data.get("data", [{}])[0]
        scores = data.get("scores", {})
 
        def add_scores(section, parent_key=None):
            updated_section = {}
            for key, value in section.items():
                if isinstance(value, dict):
                    updated_section[key] = add_scores(value, key)
                elif isinstance(value, list):
                    if key == "primary_naics_2017":
                        updated_section[key] = [
                            {"naics_code": item.get("code", ""), "naics_desc": item.get("desc", "")}
                            for item in value
                        ]
                    elif key == "primary_sic":
                        updated_section[key] = [
                            {"sic_code": item.get("code", ""), "sic_desc": item.get("desc", "")}
                            for item in value
                        ]
                    else:
                        updated_section[key] = value
                else:
                    updated_section[key] = {"value": value, "score": scores.get(key, "")}
            return updated_section
 
        # Extracting Firmographics with scores
        firmographics = add_scores(data.get("facts", {}))
 
        # Extracting Broker Details with scores
        options = data.get("options", {})
        misc = data.get("cleansed_input", {})

        broker_details = add_scores(
            {
                "broker_name": options.get("broker_name", ""),
                "broker_address": options.get("broker_address", ""),
                "broker_city": options.get("broker_city", ""),
                "broker_state": options.get("broker_state", ""),
                "broker_postal_code": options.get("broker_postal_code", ""),
                "broker_contact_points": options.get("broker_contact_points", ""),
                "broker_email": options.get("broker_email", ""),
                "broker_contact_phone": options.get("broker_contact_phone", ""),
                "submission_received_date": options.get("submission_received_date", "")
            }
        )
 
        # Extracting Product Details with scores
        product_details = add_scores(
            {
                "normalized_product": options.get(
                    "normalized_product", []
                ),  # Lists remain unchanged
                "policy_inception_date": options.get("policy_inception_date", ""),
                "end_date": options.get("end_date", ""),
                "submission_received_date": options.get("submission_received_date", ""),
                "target_premium": options.get("target_premium", ""),
                "underwriter": options.get("underwriter", ""),
                "underwriter_email": options.get("underwriter_email", ""),
                "workers_comp_estimated_annual_payroll": options.get(
                    "workers_comp_estimated_annual_payroll", ""
                ),
                "document_date": options.get("document_date", ""),
                "expiring_premium": options.get("expiring_premium", ""),
                "lob": options.get("lob", ""),
            }
        )
 
        # Extracting Limits and Coverages with scores
        limits_and_coverages = add_scores(
            {
                "100_pct_limit": options.get("100_pct_limit", {}),  # Handling nested dict
                "normalized_coverage": options.get(
                    "normalized_coverage", []
                ),  # Lists remain unchanged
                "coverage": options.get("coverage", []),  # Lists remain unchanged
                "coverage_details": json_data.get("additional_data")
            }
        )
 
        # Returning the structured data
        structured_data = {
            "Firmographics": firmographics,
            "Broker_Details": broker_details,
            "Product_Details": product_details,
            "Limits_and_Coverages": limits_and_coverages,
            "Legal_Entity_Type": ""
        }
 
        return structured_data

    def parse_property_json(self, property_json):
        parsed_data = []
 
        for item in property_json.get("data", []):
            facts = item.get("facts", {})
            options = item.get("options", {})
            scores = item.get("scores", {})
 
            # Skip entries where both building_number and location_address are missing
            if not facts.get("building_number") and not facts.get("location_address"):
                continue
 
            # Create standard_facts with scores
            standard_facts = {
                key: {"value": value, "score": scores.get(key, "")}
                for key, value in facts.items()
            }
 
            # Create limits section, ensuring only keys present in input JSON are included
            limits = {}
            if "100_pct_coverage_limits" in options:
                limits["100_pct_coverage_limits"] = {
                    k: {"value": v, "score": scores.get("100_pct_coverage_limits", "")}
                    for k, v in options["100_pct_coverage_limits"].items()
                    if k
                    in options[
                        "100_pct_coverage_limits"
                    ]  # Only include keys that exist in input
                }
 
            if "100_pct_limit" in options:
                limits["100_pct_limit"] = {
                    "value": options["100_pct_limit"],
                    "score": scores.get("100_pct_limit", ""),
                }
 
            # Create building_details section
            building_details = {
                "location_doc_id": {
                    "value": options.get("location_doc_id", ""),
                    "score": scores.get("location_doc_id", ""),
                },
                "atc_occupancy_description": {
                    "value": options.get("atc_occupancy_description", ""),
                    "score": scores.get("atc_occupancy_description", ""),
                },
            }
 
            parsed_data.append(
                {
                    "standard_facts": standard_facts,
                    "limits": limits,
                    "building_details": building_details,
                }
            )
 
        return parsed_data

    def parse_advanced_property(self, input_json):
        data = input_json
        advanced_property = []
 
        standard_facts_keys = {
            "building_number",
            "location_address",
            "location_city",
            "location_state",
            "location_postal_code",
            "location_country",
            "location_occupancy_description",
            "year_built",
        }
 
        for entry in data["data"]:
            facts = entry.get("facts", {})
            options = entry.get("options", {})
            scores = entry.get("scores", {})
 
            # Skip if both building_number and location_address are missing or empty
            if not facts.get("building_number") and not facts.get("location_address"):
                continue
 
            advanced_entry = {
                "advanced_facts": {},
                "rms_details": {},
                "atc_details": {},
                "protection_details": {},
            }
 
            # Separate standard facts and advanced facts
            for key, value in facts.items():
                if key not in standard_facts_keys:
                    advanced_entry["advanced_facts"][key] = {
                        "value": value,
                        "score": scores.get(key, ""),
                    }
 
            # Separate RMS details
            for key in ["rms_construction_code", "rms_construction_description"]:
                if key in options:
                    advanced_entry["rms_details"][key] = {
                        "value": options[key],
                        "score": scores.get(key, ""),
                    }
 
            # Separate ATC details
            for key in ["atc_construction_code", "atc_construction_description"]:
                if key in options:
                    advanced_entry["atc_details"][key] = {
                        "value": options[key],
                        "score": scores.get(key, ""),
                    }
 
            # Separate Protection details
            for key in ["burglar_alarm_type"]:
                if key in options:
                    advanced_entry["protection_details"][key] = {
                        "value": options[key],
                        "score": scores.get(key, ""),
                    }
 
            advanced_property.append(advanced_entry)
 
        return advanced_property

    def parse_general_liability(self, gl_json):
        data = gl_json
 
        first_item = data.get("data", [{}])[0]
        facts = first_item.get("facts", {})
        options = first_item.get("options", {})
        scores = first_item.get("scores", {})

        # Process gl_facts with scores
        gl_facts = {
            key: {"value": value, "score": scores.get(key, "")}
            for key, value in facts.items()
        }
 
        # Process gl_options with scores
        gl_options = {
            key: {"value": value, "score": scores.get(key, "")}
            for key, value in options.items()
        }
 
        processed_gl = {"gl_facts": gl_facts, "gl_options": gl_options}
 
        return processed_gl

    def parse_auto(self, auto_json):
        data = auto_json
        first_item = data.get("data", [{}])[0]  # Safely get first dict from list

        facts = first_item.get("facts", {})
        scores = first_item.get("scores", {})

        auto_facts = {}

        for key, value in facts.items():
            if isinstance(value, (dict, list)):
                auto_facts[key] = {"value": value, "score": scores.get(key, "")}
            else:
                auto_facts[key] = {"value": str(value), "score": scores.get(key, "")}

        return {"Auto": {"auto_facts": auto_facts}}

    # ==========================================================================
    # MAIN EXECUTION METHOD
    # ==========================================================================

    def run_sync(
        self,
        auth_token: str,
        tx_id: str,
        case_id: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Fetch submission data for a list of data packages and return structured data.
        """
        
        try:
            logger.info("Fetching message..")

            DATA_PACKAGE_IDS = self.config["data_package_ids"]
            structured_response = {}

            for dp_id in DATA_PACKAGE_IDS:
                try:
                    url = f"https://api-smartdata.di-beta.boldpenguin.com/data/v5/{dp_id}/{tx_id}"
                    headers = {
                        "Authorization": f"Bearer {auth_token}",
                        "x-api-key": self.config["api_key"],
                    }
                    response = requests.get(url, headers=headers)

                    if response.status_code == 200:
                        raw_data = response.json()

                        # Call the respective parser
                        if dp_id == "elevate-us-common-c0001":
                            structured_response["Common"] = self.parse_us_common(raw_data)
                        elif dp_id == "default-us-loss-run-c0001":
                            structured_response["Loss Run"] = raw_data.get("data", {})
                        elif dp_id == "elevate-us-property-l0001":
                            structured_response["Property"] = self.parse_property_json(raw_data)
                        elif dp_id == "default-us-admitted-advanced-property-l0001":
                            structured_response["Advanced Property"] = self.parse_advanced_property(
                                raw_data
                            )
                        elif dp_id == "elevate-us-gl-c0001":
                            structured_response["General Liability"] = self.parse_general_liability(
                                raw_data
                            )
                        elif dp_id == "elevate-us-admitted-auto-c0001":
                            structured_response["Auto"] = self.parse_auto(raw_data)
                        elif dp_id == "elevate-us-admitted-workers-comp-c0001":
                            structured_response["Workers Compensation"] = raw_data.get(
                                "data", {}
                            )

                    else:
                        logger.info(f"Failed to fetch {dp_id}: {response.status_code}")
                except Exception as e:
                    logger.info(f"Error fetching {dp_id}: {e}")

            # Save to MongoDB
            try:
                with self._get_database_connection() as db:
                    timestamp = datetime.now()
                    artifi_id = str(uuid.uuid4())

                    bp_data_doc = {
                        "artifi_id": artifi_id,
                        "tx_id": tx_id,
                        "case_id": case_id,
                        "submission_data": structured_response,
                        "history_sequence_id": 0,
                        "transaction_type": "Initial",
                        "created_at": timestamp,
                    }

                    db["BP_DATA"].insert_one(bp_data_doc)
                    logger.info(f"Record saved to BP_DATA collection with artifi_id: {artifi_id}")
            except Exception as e:
                logger.info(f"Error saving record to database: {e}")

            return structured_response
            
        except Exception as e:
            logger.error(f"Error in fetch_submission_data: {str(e)}")
            return {}


# Tool execution function for platform integration
def execute_tool(
    auth_token: str,
    tx_id: str,
    case_id: str,
    **kwargs
) -> Dict[str, Any]:
    """Execute the FetchSubmissionDataTool for platform integration."""
    tool = FetchSubmissionDataTool()
    return tool.run_sync(
        auth_token=auth_token,
        tx_id=tx_id,
        case_id=case_id,
        **kwargs
    )


# =============================================================================
# TOOL METADATA FOR STUDIO REGISTRATION
# =============================================================================

if __name__ == "__main__":
    # Test the tool
    tool = FetchSubmissionDataTool()
    
    # Test with sample data
    test_result = tool.run_sync(
        auth_token="bps_L919eLHSo5pH41RPMB5G7PNR6EXfyknJ",
        tx_id="41991b2d-fb8f-4ee0-8ca1-5d20a0c9ca81",
        case_id="SUB0010063"
    )
    
    print("=== TEST RESULT ===")
    print(json.dumps(test_result, indent=2, default=str))
    
    # Studio Blueprint metadata
    tool_metadata = {
        "class_name": "FetchSubmissionDataTool",
        "name": FetchSubmissionDataTool.name,
        "description": FetchSubmissionDataTool.description,
        "version": "1.0",
        "requires_env_vars": FetchSubmissionDataTool.requires_env_vars,
        "dependencies": FetchSubmissionDataTool.dependencies,
        "uses_llm": FetchSubmissionDataTool.uses_llm,
        "structured_output": FetchSubmissionDataTool.structured_output,
        "input_schema": FetchSubmissionDataTool.input_schema,
        "output_schema": FetchSubmissionDataTool.output_schema,
        "response_type": FetchSubmissionDataTool.response_type,
        "direct_to_user": FetchSubmissionDataTool.direct_to_user,
        "respond_back_to_agent": FetchSubmissionDataTool.respond_back_to_agent,
        "config": FetchSubmissionDataTool.config
    }

    print("\n" + "="*60)
    print("STUDIO BLUEPRINT METADATA:")
    print("="*60)
    print(json.dumps(tool_metadata, indent=2))