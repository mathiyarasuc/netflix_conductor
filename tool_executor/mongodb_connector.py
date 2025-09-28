import os
import pymongo
from pymongo import MongoClient
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class ToolDatabaseConnector:
    """MongoDB connector for tool database"""
    
    def __init__(self):
        self.client = None
        self.db = None
        self.tools_collection = None
        self._connect()
    
    def _connect(self):
        """Connect to MongoDB"""
        try:
            # Your MongoDB connection string
            connection_string = "mongodb+srv://meghansh:PEaWO49BtcE1KZ1p@artifi.0uagg19.mongodb.net/?retryWrites=true&w=majority&appName=Artifi"
            
            self.client = MongoClient(connection_string)
            
            # Test connection
            self.client.admin.command('ping')
            logger.info("✅ MongoDB connection successful")
            
            # Connect to tool_database.tools
            self.db = self.client["tool_database"]
            self.tools_collection = self.db["tools"]
            
            # Test collection access
            tool_count = self.tools_collection.count_documents({})
            logger.info(f"✅ Found {tool_count} tools in database")
            
        except Exception as e:
            logger.error(f"❌ MongoDB connection failed: {str(e)}")
            raise
    
    def get_all_tool_names(self) -> List[str]:
        """Get list of all tool names"""
        try:
            tools = self.tools_collection.find({}, {"tool_name": 1, "_id": 0})
            tool_names = [tool["tool_name"] for tool in tools if "tool_name" in tool]
            logger.info(f"📋 Retrieved {len(tool_names)} tool names")
            return sorted(tool_names)
        except Exception as e:
            logger.error(f"❌ Error fetching tool names: {str(e)}")
            return []
    
    def get_tool_details(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information for a specific tool"""
        try:
            tool = self.tools_collection.find_one({"tool_name": tool_name})
            
            if not tool:
                logger.warning(f"⚠️ Tool '{tool_name}' not found in database")
                return None
            
            # Extract key information
            tool_details = {
                "tool_name": tool.get("tool_name"),
                "description": tool.get("description", "No description available"),
                "version": tool.get("version", 1),
                "github_url": tool.get("github_url", ""),
                "input_schema": tool.get("input_schema", {}),
                "output_schema": tool.get("output_schema", {}),
                "dependencies": tool.get("dependencies", []),
                "requires_env_vars": tool.get("requires_env_vars", []),
                "uses_llm": tool.get("uses_llm", False)
            }
            
            logger.info(f"🔧 Retrieved details for tool: {tool_name}")
            return tool_details
            
        except Exception as e:
            logger.error(f"❌ Error fetching tool details for '{tool_name}': {str(e)}")
            return None
    
    def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("🔌 MongoDB connection closed")

# Global connector instance
db_connector = None

def get_db_connector():
    """Get global database connector instance"""
    global db_connector
    if db_connector is None:
        db_connector = ToolDatabaseConnector()
    return db_connector

class AgentDatabaseConnector:
    """MongoDB connector for agent database"""
    
    def __init__(self):
        self.client = None
        self.db = None
        self.agents_collection = None
        self._connect()
    
    def _connect(self):
        """Connect to MongoDB Agent Database"""
        try:
            # Same connection string as your existing tool connector
            connection_string = "mongodb+srv://meghansh:PEaWO49BtcE1KZ1p@artifi.0uagg19.mongodb.net/?retryWrites=true&w=majority&appName=Artifi"
            
            self.client = MongoClient(connection_string)
            
            # Test connection
            self.client.admin.command('ping')
            logger.info("✅ MongoDB Agent Database connection successful")
            
            # Connect to Agent_Database.AgentCatalog
            self.db = self.client["Agent_Database"]
            self.agents_collection = self.db["AgentCatalog"]
            
            # Test collection access
            agent_count = self.agents_collection.count_documents({})
            logger.info(f"✅ Found {agent_count} agents in AgentCatalog")
            
        except Exception as e:
            logger.error(f"❌ MongoDB Agent Database connection failed: {str(e)}")
            raise
    
    def get_all_agent_names(self) -> List[str]:
        """Get list of all agent names"""
        try:
            # Project only AgentName field, exclude _id
            agents = self.agents_collection.find({}, {"AgentName": 1, "_id": 0})
            agent_names = [agent["AgentName"] for agent in agents if "AgentName" in agent]
            logger.info(f"📋 Retrieved {len(agent_names)} agent names")
            return sorted(agent_names)
        except Exception as e:
            logger.error(f"❌ Error fetching agent names: {str(e)}")
            return []
    
    def get_agent_configuration(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """Get complete agent document for a specific agent - EVERYTHING"""
        try:
            # Find agent by AgentName and return EVERYTHING (no projection at all)
            agent = self.agents_collection.find_one({"AgentName": agent_name})
            
            if not agent:
                logger.warning(f"⚠️ Agent '{agent_name}' not found in AgentCatalog")
                return None
            
            # Remove MongoDB's _id field but keep everything else
            if '_id' in agent:
                del agent['_id']
            
            logger.info(f"🔧 Retrieved complete document for agent: {agent_name}")
            return agent
            
        except Exception as e:
            logger.error(f"❌ Error fetching complete document for '{agent_name}': {str(e)}")
            return None
    
    def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("🔌 MongoDB Agent Database connection closed")

# Global agent connector instance
agent_db_connector = None

def get_agent_db_connector():
    """Get global agent database connector instance"""
    global agent_db_connector
    if agent_db_connector is None:
        agent_db_connector = AgentDatabaseConnector()
    return agent_db_connector