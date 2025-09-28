const agentsResolvers = {
  Query: {
    getAgentsList: async (_parent, _args, { dataSources }) => {
      try {
        return await dataSources.agentsApi.getAgentsList();
      } catch (error) {
        throw new Error(`Error fetching agents list: ${error.message}`);
      }
    },

    getAgentDetails: async (_parent, { agentName }, { dataSources }) => {
      try {
        return await dataSources.agentsApi.getAgentDetails(agentName);
      } catch (error) {
        throw new Error(`Error fetching agent details: ${error.message}`);
      }
    }
  }
};

module.exports = agentsResolvers;