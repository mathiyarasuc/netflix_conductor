from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from mongodb_connector import get_db_connector,get_agent_db_connector
from tool_executor import get_executor  # Add this import

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
CORS(app)

import random  # Add if not already present
import requests  # Add if not already present


import json
import copy

def craft_agent_config(agent_data):
    """
    Craft agent config similar to your existing system
    """
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
        structured = raw.get("structured_output", raw) if isinstance(raw, dict) else raw
    
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
                "id": kb.get("id", ""),
                "name": kb.get("name", ""),
                "enabled": "yes",
                "collection_name": kb.get("collection_name", ""),
                "embedding_model": "BAAI/bge-small-en-v1.5",
                "description": kb.get("description", ""),
                "number_of_chunks": 5
            } if kb else {}
        },
        "isManagerAgent": agent_data.get("isManagerAgent", False),
        "selectedManagerAgents": agent_data.get("selectedManagerAgents", []),
        "managerAgentIntention": agent_data.get("managerAgentIntention", ""),
        "selectedKnowledgeBase": kb if kb else {},
        "knowledge_base": {
            "id": kb.get("id", ""),
            "name": kb.get("name", ""),
            "enabled": "yes",
            "collection_name": kb.get("collection_name", ""),
            "embedding_model": "BAAI/bge-small-en-v1.5",
            "description": kb.get("description", ""),
            "number_of_chunks": 5
        } if kb else {},
        "coreFeatures": agent_data.get("coreFeatures", {}),
        "llmProvider": agent_data.get("llmProvider", ""),
        "llmModel": agent_data.get("llmModel", "")
    }
    return agent_config


@app.route('/')
def home():
    return {"message": "Tool Executor Server Running", "status": "online"}

@app.route('/tools', methods=['GET'])
def get_all_tools():
    """Get all tool names from MongoDB database"""
    try:
        logger.info("📋 Fetching all tool names from database...")
        
        db = get_db_connector()
        tool_names = db.get_all_tool_names()
        
        return {
            "status": "success",
            "tools": tool_names,
            "count": len(tool_names),
            "message": f"Found {len(tool_names)} tools in database"
        }
    except Exception as e:
        logger.error(f"❌ Error in get_all_tools: {str(e)}")
        return {
            "status": "error",
            "message": str(e),
            "tools": []
        }, 500

@app.route('/tools/<tool_name>', methods=['GET'])
def get_tool_details(tool_name):
    """Get tool details and input schema from MongoDB"""
    try:
        logger.info(f"🔧 Fetching details for tool: {tool_name}")
        
        db = get_db_connector()
        tool_details = db.get_tool_details(tool_name)
        
        if not tool_details:
            return {
                "status": "error",
                "message": f"Tool '{tool_name}' not found in database"
            }, 404
        
        return {
            "status": "success",
            "tool_details": tool_details,
            "message": f"Retrieved details for {tool_name}"
        }
        
    except Exception as e:
        logger.error(f"❌ Error in get_tool_details: {str(e)}")
        return {
            "status": "error", 
            "message": str(e)
        }, 500

@app.route('/tools/<tool_name>/execute', methods=['POST'])
def execute_tool(tool_name):
    """Execute tool in isolated environment - COMPLETE PIPELINE"""
    try:
        logger.info(f"🚀 Executing tool: {tool_name}")
        
        # Get user input from request
        user_input = request.get_json() or {}
        logger.info(f"📝 User input: {user_input}")
        
        # Execute using complete pipeline
        executor = get_executor()
        result = executor.execute_tool(tool_name, user_input)
        
        if result["status"] == "success":
            return jsonify(result)
        else:
            return jsonify(result), 500
            
    except Exception as e:
        logger.error(f"❌ Error in execute_tool endpoint: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
    
@app.route('/agents', methods=['GET'])
def get_all_agents():
    """Get all agent names from Agent Database"""
    try:
        logger.info("📋 Fetching all agent names from Agent Database...")
        
        agent_db = get_agent_db_connector()
        agent_names = agent_db.get_all_agent_names()
        
        return {
            "status": "success",
            "agents": agent_names,
            "count": len(agent_names),
            "message": f"Found {len(agent_names)} agents in database"
        }
    except Exception as e:
        logger.error(f"❌ Error in get_all_agents: {str(e)}")
        return {
            "status": "error",
            "message": str(e),
            "agents": []
        }, 500

@app.route('/agents/<agent_name>/configuration', methods=['GET'])
def get_agent_configuration(agent_name):
    """Get complete agent document for specific agent"""
    try:
        logger.info(f"🔧 Fetching complete document for agent: {agent_name}")
        
        agent_db = get_agent_db_connector()
        complete_agent = agent_db.get_agent_configuration(agent_name)
        
        if complete_agent is None:
            return {
                "status": "error",
                "message": f"Agent '{agent_name}' not found in database"
            }, 404
        
        # Return just the raw agent document
        return complete_agent
        
    except Exception as e:
        logger.error(f"❌ Error in get_agent_configuration: {str(e)}")
        return {
            "status": "error", 
            "message": str(e)
        }, 500

@app.route('/agents/<agent_name>/execute', methods=['POST'])
def execute_agent(agent_name):
    """
    Execute agent using your proven orchestration approach
    """
    try:
        logger.info(f"🚀 Executing agent: {agent_name}")
        
        # Get user input from frontend
        user_input = request.get_json() or {}
        thread_id = user_input.get('thread_id')
        message = user_input.get('message')
        
        # Ensure thread_id is an integer
        if thread_id is None or thread_id == "":
            thread_id = random.randint(1, 100000)
        else:
            try:
                thread_id = int(thread_id)
            except (ValueError, TypeError):
                thread_id = random.randint(1, 100000)
        
        logger.info(f"📝 User input - Thread ID: {thread_id}, Message: {message}")
        
        # Fetch complete agent record from MongoDB
        agent_db = get_agent_db_connector()
        complete_agent = agent_db.get_agent_configuration(agent_name)
        
        if complete_agent is None:
            return {
                "status": "error",
                "message": f"Agent '{agent_name}' not found in database"
            }, 404
        
        logger.info(f"✅ Retrieved complete agent record for: {agent_name}")
        
        # ✅ CRAFT AGENT CONFIG using your proven method
        agent_config = craft_agent_config(complete_agent)
        
        logger.info(f"🔧 Crafted agent config with structured_output: {bool(agent_config['Configuration'].get('structured_output'))}")
        
        # Prepare payload for FastAPI endpoint (matching your system)
        fastapi_payload = {
            "agent_id": agent_config.get("AgentID"), #replaced with agent_id
            "message": message,
            "thread_id": thread_id
        }
        
        logger.info(f"🚀 Posting to FastAPI endpoint...")
        logger.info(f"📋 Payload structure: agent_config keys: {list(agent_config.keys())}")
        
        # POST to FastAPI endpoint
        fastapi_url = "http://16.170.162.72:8000/query"
        
        response = requests.post(
            fastapi_url,
            json=fastapi_payload,
            headers={'Content-Type': 'application/json'},
            timeout=300
        )
        
        logger.info(f"📡 FastAPI response status: {response.status_code}")
        
        if response.status_code == 200:
            raw_response = response.json()
            
            # ✅ OPTIONAL: Apply your markdown conversion if needed
            def convert_section(val):
                if isinstance(val, str):
                    # You can add markdown.markdown(val, extensions=['extra']) here if needed
                    return val
                if isinstance(val, dict):
                    if "result" in val:
                        # Convert markdown to HTML if needed
                        pass
                    return val
                return val
            
            # Apply conversion to response fields
            for k, v in raw_response.items():
                raw_response[k] = convert_section(v)
            
            return jsonify(raw_response), 200
        else:
            error_details = response.text
            logger.error(f"❌ FastAPI error: {error_details}")
            return {
                "status": "error",
                "message": f"FastAPI endpoint returned status {response.status_code}",
                "details": error_details
            }, response.status_code
            
    except Exception as e:
        logger.error(f"❌ Error in execute_agent: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }, 500



if __name__ == '__main__':    
    app.run(debug=True, host='0.0.0.0', port=7000)
