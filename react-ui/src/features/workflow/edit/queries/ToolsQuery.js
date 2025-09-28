import { gql } from '@apollo/client'

export const TOOLS_LIST_QUERY = gql`
  query GetToolsList {
    getToolsList {
      status
      tools
      count
    }
  }
`

export const TOOL_DETAILS_QUERY = gql`
  query GetToolDetails($toolName: String!) {
    getToolDetails(toolName: $toolName) {
      status
      message
      tool_details {
        tool_name
        description
        input_schema
        output_schema
        version
        uses_llm
        dependencies
        requires_env_vars
      }
    }
  }
`