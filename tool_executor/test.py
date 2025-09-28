#!/usr/bin/env python3

import copy
import json
import random
import markdown
import requests
import sys
from typing import Dict, Any

# Mock the functions from your codebase
def log_message(task_id, message):
    """Mock log_message function"""
    print(f"[{task_id}] {message}")

# Mock MongoDB client
class MockClient:
    def __init__(self):
        pass
    
    def __getitem__(self, db_name):
        return MockDB()

class MockDB:
    def __getitem__(self, collection_name):
        return MockCollection()

class MockCollection:
    def find(self, query):
        # Mock agent data - return all agents from TARGET_AGENT_IDS
        mock_agents = [
            {
                "AgentID": "62bdca88-828e-48a2-ac10-357264372043",
                "AgentName": "InsuranceVerify", 
                "Configuration": {},
                "selectedKnowledgeBase": None
            },
            {
                "AgentID": "10645287-854e-4270-bb7d-fcbb31d3aefa",
                "AgentName": "LossInsights",
                "Configuration": {},
                "selectedKnowledgeBase": None
            },
            {
                "AgentID": "8c72ba1d-9403-4782-8f8c-12564ab73f9c",
                "AgentName": "PropEval",
                "Configuration": {},
                "selectedKnowledgeBase": None
            },
            {
                "AgentID": "5cbb17d3-5fe5-4b59-9d4b-b33d471e4220",
                "AgentName": "ExposureInsights",
                "Configuration": {},
                "selectedKnowledgeBase": None
            },
            {
                "AgentID": "48e0fde3-2c69-44f0-98d6-b6a5b031c2bb",
                "AgentName": "EligibilityCheck",
                "Configuration": {},
                "selectedKnowledgeBase": None
            },
            {
                "AgentID": "383daaad-4b46-491b-b987-9dd17d430ca3",
                "AgentName": "BusineesProfileSearch",
                "Configuration": {},
                "selectedKnowledgeBase": None
            }
        ]
        return mock_agents

# Mock client and save_report_data
client = MockClient()

def save_report_data(submission_data, artifi_id, tx_id):
    """Mock save_report_data function"""
    print(f"Mock: save_report_data called with artifi_id={artifi_id}, tx_id={tx_id}")

# Mock task class
class MockTask:
    def __init__(self, task_id, input_data):
        self.task_id = task_id
        self.input_data = input_data

# Your original constants
TARGET_AGENT_IDS = {
    "10645287-854e-4270-bb7d-fcbb31d3aefa",  # LossInsight (case id)
    "5cbb17d3-5fe5-4b59-9d4b-b33d471e4220",  # ExposureInsight (case id)
    "48e0fde3-2c69-44f0-98d6-b6a5b031c2bb",  # EligibilityCheck
    "62bdca88-828e-48a2-ac10-357264372043",  # InsuranceVerify (case id)
    "8c72ba1d-9403-4782-8f8c-12564ab73f9c",  # PropEval
    "383daaad-4b46-491b-b987-9dd17d430ca3"   # BusineesProfileSearch
}

AGENT_PROMPTS = {
    "LossInsights":       "Please provide loss insights for the data.",
    "ExposureInsights":   "Please provide exposure insights for the data.",
    "EligibilityCheck":  "Please check eligibility based on the data.",
    "InsuranceVerify": "Please verify insurance details in the data.",
    "PropEval":          "Please provide Property evaluation insights for the data.",
    "BusineesProfileSearch": "Please search the business profile based on the data.",
}

def deep_update(original: dict, updates: dict) -> dict:
    """
    Recursively walk `original`. Whenever you encounter a key that's in `updates`:
      - if original[k] is a dict with a 'value' key, replace original[k]['value'] and update 'score' if present
      - otherwise replace original[k] outright.
    Returns the mutated `original`.
    """
    
    # Create a case-insensitive lookup for updates
    updates_lower = {k.lower(): (k, v) for k, v in updates.items()}
    
    for k, v in list(original.items()):
        # Check if this key needs updating (case-insensitive)
        if k.lower() in updates_lower:
            original_key, new_val = updates_lower[k.lower()]
            if isinstance(original[k], dict) and 'value' in original[k]:
                original[k]['value'] = new_val
                # Update score if it exists, otherwise set a default score
                if 'score' in original[k]:
                    original[k]['score'] = "100"
            else:
                original[k] = new_val

        # If the value is itself a dict, recurse into it
        if isinstance(original[k], dict):
            deep_update(original[k], updates)  # Pass original updates, function will recreate the lookup

    return original

def craft_agent_config(agent_data):
    cfg = agent_data.get("Configuration", {})
    kb = agent_data.get("selectedKnowledgeBase")
    toggle = cfg.get("structured_output_toggle", False)
    raw = cfg.get("structured_output", "{}")

    if not toggle:
        structured = {}
    elif isinstance(raw, bool) and not raw:
        structured = None
    elif isinstance(raw, str):
        try:
            structured = json.loads(raw)
            structured = structured.get("structured_output", structured)
        except:
            structured = {}
    else:
        structured = raw.get("structured_output", raw) if raw else {}

    agent_config = {
        "AgentID": agent_data.get("AgentID", ""),
        "AgentName": agent_data.get("AgentName", ""),
        "AgentDesc": agent_data.get("AgentDesc", ""),
        "CreatedOn": agent_data.get("CreatedOn", ""),
        "Configuration": {
            "name": cfg.get("name", ""),
            "function_description": cfg.get("function_description", ""),
            "system_message": cfg.get("system_message", ""),
            "tools": cfg.get("tools", []),
            "category": cfg.get("category", ""),
            "structured_output": structured,
            "knowledge_base": {
                "id": kb.get("id", "") if kb else "",
                "name": kb.get("name", "") if kb else "",
                "enabled": "yes",
                "collection_name": kb.get("collection_name", "") if kb else "",
                "embedding_model": "BAAI/bge-small-en-v1.5",
                "description": kb.get("description", "") if kb else "",
                "number_of_chunks": 5
            } if kb else {}
        },
        "isManagerAgent": agent_data.get("isManagerAgent", False),
        "selectedManagerAgents": agent_data.get("selectedManagerAgents", []),
        "managerAgentIntention": agent_data.get("managerAgentIntention", ""),
        "selectedKnowledgeBase": kb if kb else {},
        "knowledge_base": {
            "id": kb.get("id", "") if kb else "",
            "name": kb.get("name", "") if kb else "",
            "enabled": "yes",
            "collection_name": kb.get("collection_name", "") if kb else "",
            "embedding_model": "BAAI/bge-small-en-v1.5",
            "description": kb.get("description", "") if kb else "",
            "number_of_chunks": 5
        } if kb else {},
        "coreFeatures": agent_data.get("coreFeatures", {}),
        "llmProvider": agent_data.get("llmProvider", ""),
        "llmModel": agent_data.get("llmModel", "")
    }

    return agent_config

# Your exact call_ven_agent_service function
def call_ven_agent_service(task):
    task_id    = task.task_id
    input_data = task.input_data or {}
    submission = input_data.get("submission_data", {})
    thread_id  = input_data.get("thread_id", random.randint(1,100000))

    if thread_id is None or thread_id == "":
        thread_id = random.randint(1, 100000)
    else:
        try:
            thread_id = int(thread_id)  # Convert to int
        except (ValueError, TypeError):
            thread_id = random.randint(1, 100000)
    
    log_message(task_id, f"Using thread_id: {thread_id} (type: {type(thread_id)})")

    case_id = input_data.get("case_id", "")

    log_message(task_id, f"Calling agents for case_id: {case_id}")

    agents = client["Agent_Database"]["AgentCatalog"].find({
        "AgentID": {"$in": list(TARGET_AGENT_IDS)}
    })

    # helper: safely convert markdown→HTML
    def md2html(s: str) -> str:
        return markdown.markdown(s, extensions=['extra'])

    # convert top-level sections like in the rerun function
    def convert_section(val):
        if isinstance(val, str):
            return md2html(val)
        if isinstance(val, dict):
            if "result" in val:
                val["result"] = md2html(val["result"])
            elif isinstance(val, str):
                val["response"] = md2html(val["response"])
            return val
        return val

    # Mapping of AgentIDs to their specific endpoints
    agent_endpoints = {
        "62bdca88-828e-48a2-ac10-357264372043": "https://insuranceverify.enowclear360.com/query",  # DataAnalysis (InsuranceVerify)
        "10645287-854e-4270-bb7d-fcbb31d3aefa": "https://lossinsights.enowclear360.com/query",  # LossInsights
        "8c72ba1d-9403-4782-8f8c-12564ab73f9c": "https://propeval.enowclear360.com/query",  # PropEval (Analytics 2)
        "5cbb17d3-5fe5-4b59-9d4b-b33d471e4220": "https://exposureinsights.enowclear360.com/query",  # ExposureInsights
        "48e0fde3-2c69-44f0-98d6-b6a5b031c2bb": "https://eligibility.enowclear360.com/query",  # Appetite and Eligibility
        "383daaad-4b46-491b-b987-9dd17d430ca3": "https://businessprofile.enowclear360.com/query",  # Business Operations (Analytics 1)
    }

    # Default endpoint for agents not specified in the mapping
    default_endpoint = "http://54.80.147.224:9000/query"

    results = {}
    for agent in agents:
        agent_id   = agent.get("AgentID")
        agent_name = agent.get("AgentName", agent["AgentID"])
        agent_cfg  = craft_agent_config(agent)
        suffix     = AGENT_PROMPTS.get(agent_name, "")

        #new agents with case id getting only required data
        if agent_id == "62bdca88-828e-48a2-ac10-357264372043": # DataAnalysis (InsuranceVerify) case id
            # Send common
            sub_data = f"case_id : {case_id}"

        elif agent_id == "10645287-854e-4270-bb7d-fcbb31d3aefa": # LossInsights
            # Only send Common + Loss Run
            sub_data = f"case_id : {case_id}"

        elif agent_id == "8c72ba1d-9403-4782-8f8c-12564ab73f9c": # PropEval (Analytics 2)
            # Only send Common + Property + Advanced Property
            sub_data = f"case_id : {case_id}"       

        elif agent_id == "5cbb17d3-5fe5-4b59-9d4b-b33d471e4220": # ExposureInsights
            # Only send submission data without LossRun
            sub_data = f"case_id : {case_id}" 

        elif agent_id == "48e0fde3-2c69-44f0-98d6-b6a5b031c2bb": # Appetite and Eligibility
            # Only send submission data without LossRun
            sub_data = submission.copy()
            sub_data.pop("Loss Run", None)

        elif agent_id == "383daaad-4b46-491b-b987-9dd17d430ca3": # Business Operations (Analytics 1)
            # Only send Common within Submission Data
            sub_data = {
                "Common": submission.get("Common")
            }

        else:
            # Default case, send the entire submission
            sub_data = submission

        full_message = f"{sub_data} {suffix}".strip()
        log_message(task_id, f"sending to {agent_name!r}")

        try:
            # Select endpoint based on agent_id, fallback to default if not found
            endpoint = agent_endpoints.get(agent_id, default_endpoint)
            log_message(task_id, f"POST to {endpoint}")
            log_message(task_id, f"Payload: {json.dumps({'message': full_message, 'thread_id': thread_id}, indent=2)}")
            
            # Make the actual API call (you can comment this out for dry-run testing)
            r = requests.post(
                endpoint,
                json={
                    # "agent_config": agent_cfg,
                    "message":      full_message,
                    "thread_id":    thread_id
                },
                timeout=300
            )
            raw = r.json()

            # apply markdown→HTML conversion to each top-level field
            for k, v in raw.items():
                raw[k] = convert_section(v)

            results[agent_name] = raw

        except Exception as e:
            log_message(task_id, f"Error calling {agent_name}: {str(e)}")
            results[agent_name] = {"error": str(e)}

    return results

# Test function
def test_call_ven_agent_service(input_data):
    """Test the call_ven_agent_service function with large JSON payload"""
    print("=" * 80)
    print("TESTING call_ven_agent_service")
    print("=" * 80)
    
    task = MockTask("test_task_large_json", input_data)
    
    # Print summary of input data instead of full JSON (since it's 21k lines)
    print(f"Input Data Summary:")
    print(f"  - case_id: {input_data.get('case_id', 'NOT SET')}")
    print(f"  - thread_id: {input_data.get('thread_id', 'NOT SET')}")
    print(f"  - submission_data keys: {list(input_data.get('submission_data', {}).keys()) if input_data.get('submission_data') else 'NO SUBMISSION_DATA'}")
    
    if input_data.get('submission_data'):
        sub_data = input_data['submission_data']
        print(f"  - submission_data size: ~{len(str(sub_data))} characters")
        if 'Common' in sub_data:
            print(f"  - Common data keys: {list(sub_data['Common'].keys()) if isinstance(sub_data['Common'], dict) else 'Not a dict'}")
    
    print("-" * 80)
    
    result = call_ven_agent_service(task)
    
    print("RESULTS SUMMARY:")
    for agent_name, agent_result in result.items():
        if "error" in agent_result:
            print(f"  - {agent_name}: ERROR - {agent_result['error']}")
        else:
            print(f"  - {agent_name}: SUCCESS - {len(str(agent_result))} chars response")
    
    print("=" * 80)
    return result

def load_json_file(filepath):
    """Load JSON data from file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"File not found: {filepath}")
        return None
    except json.JSONDecodeError as e:
        print(f"Invalid JSON in file {filepath}: {e}")
        return None
    except Exception as e:
        print(f"Error reading file {filepath}: {e}")
        return None

def main():
    """Main test function"""
    print("call_ven_agent_service Test Script for Large JSON")
    print("Usage:")
    print("  python script.py <json_file_path>")
    print("  python script.py '<json_string>'")
    print()
    
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        
        # Check if it's a file path or JSON string
        if arg.endswith('.json') or '/' in arg or '\\' in arg:
            # Treat as file path
            print(f"Loading JSON from file: {arg}")
            input_data = load_json_file(arg)
            if input_data is None:
                sys.exit(1)
        else:
            # Treat as JSON string
            try:
                input_data = json.loads(arg)
                print("Using provided JSON string")
            except json.JSONDecodeError:
                print("Invalid JSON string provided")
                sys.exit(1)
        
        test_call_ven_agent_service(input_data)
        
    else:
        # Default test with minimal data
        print("No input provided. Using minimal test data.")
        print("To test with your 21k line JSON:")
        print("  python script.py data.json")
        print("  python script.py '{\"case_id\":\"SUB123\", \"submission_data\":{...}}'")
        
        minimal_data = {
            "case_id": "TEST001",
            "thread_id": 12345,
            "submission_data": {
                "Common": {
                    "business_name": "Test Business",
                    "legal_entity_type": {"value": "llc", "score": "90"}
                },
                "Property": {"some": "property data"},
                "Loss Run": {"some": "loss data"}
            }
        }
        
        test_call_ven_agent_service(minimal_data)

if __name__ == "__main__":
    main()