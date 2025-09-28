const ConductorApi = require("../../../utils/conductorApi");

class ToolsApi extends ConductorApi {
  constructor() {
    super();
    this.baseURL = process.env.TOOLS_API_URL;
  }

  async getToolsList() {
    try {
      return await this.get('/tools');
    } catch (error) {
      throw new Error(`Failed to fetch tools list: ${error.message}`);
    }
  }

  async getToolDetails(toolName) {
    try {
      const response = await this.get(`/tools/${toolName}`);
      
      // ✅ SIMPLE - just return what we need
      if (response.tool_details) {
        return {
          status: response.status,
          message: response.message,
          tool_details: {
            tool_name: response.tool_details.tool_name,
            input_schema: response.tool_details.input_schema  // ✅ ONLY this matters!
          }
        };
      }
      
      return response;
    } catch (error) {
      throw new Error(`Failed to fetch tool details for ${toolName}: ${error.message}`);
    }
  }
}

module.exports = ToolsApi;