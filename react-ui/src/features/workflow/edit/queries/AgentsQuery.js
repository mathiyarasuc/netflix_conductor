import { gql } from '@apollo/client'

export const AGENTS_LIST_QUERY = gql`
  query GetAgentsList {
    getAgentsList {
      status
      agents
      count
    }
  }
`

export const AGENT_DETAILS_QUERY = gql`
  query GetAgentDetails($agentName: String!) {
    getAgentDetails(agentName: $agentName) {
      AgentID
      AgentName
      AgentDesc
      CreatedOn
      Configuration
      coreFeatures
      isManagerAgent
      knowledge_base
      llmModel
      llmProvider
      managerAgentIntention
      selectedKnowledgeBase
      selectedManagerAgents
    }
  }
`
