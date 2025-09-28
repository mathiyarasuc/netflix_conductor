const ConductorApi = require("../../../utils/conductorApi");

class AgentsApi extends ConductorApi {
  constructor() {
    super();
    this.baseURL = process.env.AGENTS_API_URL;
  }

  async getAgentsList() {
    try {
      return await this.get('/agents');
    } catch (error) {
      throw new Error(`Failed to fetch agents list: ${error.message}`);
    }
  }

  async getAgentDetails(agentName) {
    try {
      // This calls your endpoint that returns the complete agent document
      const response = await this.get(`/agents/${agentName}/configuration`);
      
      // Since your endpoint returns the raw agent document,
      // we just return it directly
      return response;
    } catch (error) {
      throw new Error(`Failed to fetch agent details for ${agentName}: ${error.message}`);
    }
  }
}

module.exports = AgentsApi;