from flask import Flask, request, jsonify
import json
from datetime import datetime
import time

app = Flask(__name__)

@app.route('/agents/<agent_name>/execute', methods=['POST'])
def agent_execute(agent_name):
    """
    Dummy endpoint that receives agent execution requests from Netflix Conductor
    """
    try:
        # Get the JSON data from the request
        data = request.get_json()
        
        # Print timestamp for tracking
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print("=" * 60)
        print(f"🤖 AGENT EXECUTION REQUEST - {timestamp}")
        print("=" * 60)
        print(f"Agent Name: {agent_name}")
        print(f"Request Headers: {dict(request.headers)}")
        print(f"Request Data:")
        print(json.dumps(data, indent=2))
        print("=" * 60)
        
        # Extract specific fields if they exist
        if data:
            thread_id = data.get('thread_id', 'Not provided')
            message = data.get('message', 'Not provided')
            agent_name_from_data = data.get('agent_name', 'Not provided')
            
            print(f"📝 Extracted Parameters:")
            print(f"   Thread ID: {thread_id}")
            print(f"   Message: {message}")
            print(f"   Agent Name (from data): {agent_name_from_data}")
            print("=" * 60)
        
        # Simulate processing time (optional)
        # time.sleep(1)
        
        # Return success response
        response = {
            'status': 'success',
            'message': f'Agent {agent_name} executed successfully',
            'agent_name': agent_name,
            'thread_id': data.get('thread_id') if data else None,
            'processed_at': timestamp,
            'execution_result': {
                'output': f'Agent {agent_name} processed message: {data.get("message", "No message")}',
                'success': True
            }
        }
        
        print(f"✅ Sending SUCCESS response:")
        print(json.dumps(response, indent=2))
        print("=" * 60)

        time.sleep(20)
        
        return jsonify(response), 200
        
    except Exception as e:
        # Handle any errors
        error_response = {
            'status': 'error',
            'message': f'Failed to execute agent {agent_name}',
            'error': str(e),
            'agent_name': agent_name,
            'processed_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        print(f"❌ ERROR occurred:")
        print(json.dumps(error_response, indent=2))
        print("=" * 60)
        
        return jsonify(error_response), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Agent dummy server is running',
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }), 200

@app.route('/agents', methods=['GET'])
def list_agents():
    """List available agents (dummy data)"""
    return jsonify({
        'status': 'success',
        'agents': ['agent1', 'agent2', 'test_agent'],
        'count': 3
    }), 200

if __name__ == '__main__':
    print("🚀 Starting Agent Dummy Server...")
    print("📡 Listening on: http://0.0.0.0:9000")
    print("🎯 Agent execution endpoint: POST /agents/<agent_name>/execute")
    print("❤️  Health check: GET /health")
    print("📋 List agents: GET /agents")
    print("=" * 60)
    
    # Run Flask server on all interfaces, port 7000
    app.run(host='0.0.0.0', port=9000, debug=True)
