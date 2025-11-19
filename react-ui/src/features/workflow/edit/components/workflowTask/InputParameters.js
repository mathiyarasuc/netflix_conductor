import React, { useState, useEffect, useMemo, useCallback } from 'react'
import PropTypes from 'prop-types'
import { get } from '@totalsoft/rules-algebra-react'
import { Grid, Typography, Divider } from '@mui/material'
import { useLazyQuery } from '@apollo/client'
import { TOOL_DETAILS_QUERY } from '../../queries/ToolsQuery'
import InputParametersList from './InputParametersList'
import { nodeConfig } from 'features/designer/constants/NodeConfig'
import LambdaNodeInputParameters from 'features/designer/nodeModels/lambdaNode/LambdaNodeInputParameters'
import HttpNodeInputParameters from 'features/designer/nodeModels/httpNode/HttpNodeInputParameters'
import InputParametersHeader from './InputParametersHeader'
import EventNodeInputParameters from 'features/designer/nodeModels/eventNode/EventNodeInputParameters'
import ToolParameterForm from './ToolParameterForm'
import AgentParameterForm from './AgentParameterForm'

const InputParameters = ({
  inputParametersLens,
  inputTemplate,
  nodeType,
  onPayloadChange,
  previousNodes,
  currentNodeId,
  currentTaskRef
}) => {
  const [toolSchema, setToolSchema] = useState(null)
  const [loadingSchema, setLoadingSchema] = useState(false)
  const [currentToolName, setCurrentToolName] = useState(null)

  const [runToolDetailsQuery, { loading: loadingToolDetails, data: toolDetailsData }] = useLazyQuery(TOOL_DETAILS_QUERY)

const filteredPreviousNodes = useMemo(() => {
  if (!Array.isArray(previousNodes) || previousNodes.length === 0) return []

  // ✅ FIXED: Added node?.inputs?. prefix to access nested properties correctly
  const normalizedNodes = previousNodes.map(node => ({
    id: node?.getID?.() || node?.id || node?.options?.id || null,
    ref: node?.inputs?.taskReferenceName || node?.taskReferenceName || node?.options?.taskReferenceName || node?.name || null,
    type: node?.inputs?.type || node?.type || node?.options?.type || null,
    raw: node
  }))

  // Find index of the current node by ID or taskReferenceName
  const currentIndex = normalizedNodes.findIndex(
    n => n.id === currentNodeId || n.ref === currentTaskRef
  )

  // If current node not found, assume it's at the end
  const beforeNodes =
    currentIndex > 0
      ? normalizedNodes.slice(0, currentIndex)
      : currentIndex === 0
      ? []
      : normalizedNodes

  // Exclude START/END nodes safely
  const filtered = beforeNodes.filter(
    n => !['START', 'END'].includes(n.ref)
  )

  // Return original node objects
  return filtered.map(n => n.raw)
}, [previousNodes, currentNodeId, currentTaskRef])


  // Memoize current parameters to prevent unnecessary re-renders
  const currentParams = useMemo(() => {
    return inputParametersLens |> get
  }, [inputParametersLens])

  // Memoize tool detection logic
  const toolInfo = useMemo(() => {
    if (nodeType !== 'HTTP') return null

    const httpRequest = currentParams?.http_request

    if (!httpRequest?.uri?.includes('/tools/') || !httpRequest?.uri?.includes('/execute')) {
      return null
    }

    const matches = httpRequest.uri.match(/\/tools\/([^/]+)\/execute/)
    const result = matches && matches[1] ? { toolName: matches[1] } : null
    return result
  }, [nodeType, currentParams])

  // Memoize agent detection logic (add this after tool detection)
  const agentInfo = useMemo(() => {
    if (nodeType !== 'HTTP') return null

    const httpRequest = currentParams?.http_request

    if (!httpRequest?.uri?.includes('/agents/') || !httpRequest?.uri?.includes('/execute')) {
      return null
    }

    const matches = httpRequest.uri.match(/\/agents\/([^/]+)\/execute/)
    const result = matches && matches[1] ? { agentName: matches[1] } : null

    return result
  }, [nodeType, currentParams])

  useEffect(() => {
    if (!toolInfo?.toolName) {
      setToolSchema(null)
      setCurrentToolName(null)
      return
    }

    // Only fetch if tool name changed
    if (toolInfo.toolName === currentToolName) return

    setCurrentToolName(toolInfo.toolName)
    setLoadingSchema(true)

    // ✅ USE GraphQL QUERY instead of fetch:
    runToolDetailsQuery({
      variables: { toolName: toolInfo.toolName }
    })
  }, [toolInfo?.toolName, currentToolName, runToolDetailsQuery])

  useEffect(() => {
    if (toolDetailsData?.getToolDetails?.status === 'success') {
      const schema = toolDetailsData.getToolDetails.tool_details?.input_schema
      setToolSchema(schema)
      setLoadingSchema(false)
    } else if (toolDetailsData && toolDetailsData.getToolDetails?.status !== 'success') {
      console.error('❌ Failed to fetch tool schema via GraphQL')
      setToolSchema(null)
      setLoadingSchema(false)
    }
  }, [toolDetailsData])
  
  // Memoize the tool parameter form to prevent unnecessary re-renders
  const toolParameterForm = useMemo(() => {
    if (nodeType !== 'HTTP' || !toolSchema) {
      return null
    }

    return (
      <Grid container spacing={2}>
        <Grid item xs={12}>
          <Typography variant='h6' style={{ marginBottom: '20px', color: '#4caf50' }}>
            🔧 Tool Parameters
          </Typography>
          {loadingSchema || loadingToolDetails ? (
            <Typography>Loading tool schema...</Typography>
          ) : (
            <ToolParameterForm schema={toolSchema} inputParametersLens={inputParametersLens} previousNodes={filteredPreviousNodes} />
          )}
        </Grid>
      </Grid>
    )
  }, [nodeType, toolSchema, loadingSchema, loadingToolDetails, inputParametersLens, filteredPreviousNodes])

  // Memoize the agent parameter form (add this after tool parameter form)
  const agentParameterForm = useMemo(() => {
    if (nodeType !== 'HTTP' || !agentInfo) {
      return null
    }

    return (
      <Grid container spacing={2}>
        <Grid item xs={12}>
          <Typography variant='h6' style={{ marginBottom: '20px', color: '#9c27b0' }}>
            🤖 Agent Parameters
          </Typography>
          <AgentParameterForm agentName={agentInfo.agentName} inputParametersLens={inputParametersLens} previousNodes={filteredPreviousNodes} />
        </Grid>
      </Grid>
    )
  }, [nodeType, agentInfo, inputParametersLens, filteredPreviousNodes])

  // Memoize the regular input parameters renderer (BEFORE any returns)
  const renderInputParameters = useCallback(
    type => {
      switch (type) {
        case nodeConfig.HTTP.type:
          return (
            <HttpNodeInputParameters
              httpRequestLens={
                inputParametersLens?.http_request |> get ? inputParametersLens?.http_request : inputParametersLens?.httpRequest
              }
            />
          )
        case nodeConfig.LAMBDA.type:
          return (
            <>
              <InputParametersHeader inputParametersLens={inputParametersLens} />
              <Divider style={{ marginTop: '10px', marginBottom: '10px' }} />
              <InputParametersList inputParametersLens={inputParametersLens} />
              <LambdaNodeInputParameters inputParametersLens={inputParametersLens} />
            </>
          )
        case nodeConfig.EVENT.type:
          return <EventNodeInputParameters inputParametersLens={inputParametersLens} onPayloadChange={onPayloadChange} />
        default:
          return (
            <>
              <InputParametersHeader inputParametersLens={inputParametersLens} />
              <Divider style={{ marginTop: '10px', marginBottom: '10px' }} />
              <InputParametersList inputParametersLens={inputParametersLens} inputTemplate={inputTemplate} />
            </>
          )
      }
    },
    [inputParametersLens, inputTemplate, onPayloadChange]
  )

  // Return tool form if this is a tool
  if (toolParameterForm) {
    return toolParameterForm
  }

  // Return agent form if this is an agent
  if (agentParameterForm) {
    return agentParameterForm
  }

  return renderInputParameters(nodeType)
}

InputParameters.propTypes = {
  inputParametersLens: PropTypes.object.isRequired,
  inputTemplate: PropTypes.object,
  nodeType: PropTypes.string.isRequired,
  onPayloadChange: PropTypes.func.isRequired,
  previousNodes: PropTypes.array,
  currentNodeId: PropTypes.string,
  currentTaskRef: PropTypes.string
}

export default InputParameters