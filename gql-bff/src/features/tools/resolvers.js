const toolsResolvers = {
  Query: {
    getToolsList: async (_parent, _args, { dataSources }) => {
      try {
        return await dataSources.toolsApi.getToolsList();
      } catch (error) {
        throw new Error(`Error fetching tools list: ${error.message}`);
      }
    },

    getToolDetails: async (_parent, { toolName }, { dataSources }) => {
      try {
        return await dataSources.toolsApi.getToolDetails(toolName);
      } catch (error) {
        throw new Error(`Error fetching tool details: ${error.message}`);
      }
    }
  }
};

module.exports = toolsResolvers;