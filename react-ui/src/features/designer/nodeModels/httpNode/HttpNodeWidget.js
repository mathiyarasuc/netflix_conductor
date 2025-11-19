import React, { useMemo } from 'react'
import PropTypes from 'prop-types'
import { PortWidget } from '@projectstorm/react-diagrams'
import { nodeConfig } from 'features/designer/constants/NodeConfig'

import HttpIcon from '@mui/icons-material/Http'
import BuildIcon from '@mui/icons-material/Build'
import SmartToyIcon from '@mui/icons-material/SmartToy'
import AgentNodeWidget from './AgentNodeWidget'

export const HttpNodeWidget = ({ node, engine }) => {
  const baseNodeType = node?.type1 || 'HTTP'

  const currentParams = useMemo(() => {
    try {
      return node?.inputs?.inputParameters || node?.inputs || {}
    } catch {
      return {}
    }
  }, [node])

  const toolInfo = useMemo(() => {
    const httpRequest = currentParams?.http_request
    if (!httpRequest?.uri?.includes('/tools/') || !httpRequest?.uri?.includes('/execute')) return null

    const matches = httpRequest.uri.match(/\/tools\/([^/]+)\/execute/)
    return matches?.[1] ? { toolName: matches[1] } : null
  }, [currentParams])

  const agentInfo = useMemo(() => {
    const httpRequest = currentParams?.http_request
    if (!httpRequest?.uri?.includes('/agents/') || !httpRequest?.uri?.includes('/execute')) return null

    const matches = httpRequest.uri.match(/\/agents\/([^/]+)\/execute/)
    return matches?.[1] ? { agentName: matches[1] } : null
  }, [currentParams])

  const effectiveType = useMemo(() => {
    if (agentInfo) return 'AGENT'
    if (toolInfo) return 'TOOL'
    return baseNodeType
  }, [agentInfo, toolInfo, baseNodeType])

  if (effectiveType === 'AGENT') {
    return <AgentNodeWidget node={node} engine={engine} />
  }

  const config = nodeConfig[effectiveType] || nodeConfig.HTTP
  const { color, iconColor } = config

  const { name } = node.inputs || {}

  const iconMap = {
    TOOL: BuildIcon,
    AGENT: SmartToyIcon,
    HTTP: HttpIcon
  }

  const IconComponent = iconMap[effectiveType] || HttpIcon

  const style = {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'flex-start',
    backgroundColor: '#fff',
    border: `1px solid ${iconColor || '#ccc'}`,
    borderRadius: '12px',
    padding: '6px 8px',
    position: 'relative',
    minWidth: '140px',
    gap: '8px'
  }

  return (
    <div className='http-node' style={style}>
      <div style={{ position: 'absolute', left: -10, top: '40%' }}>
        <PortWidget engine={engine} port={node?.getPort('in')}>
          <div
            style={{
              width: 14,
              height: 14,
              borderRadius: '50%',
              backgroundColor: '#fff',
              border: '1px solid #000',
              cursor: 'pointer'
            }}
          />
        </PortWidget>
      </div>

      {IconComponent && (
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            backgroundColor: color || '#1565C0',
            borderRadius: '10px',
            width: '36px',
            height: '36px',
            flexShrink: 0
          }}
        >
          <IconComponent style={{ color: iconColor }} fontSize='small' />
        </div>
      )}

      <div style={{ display: 'flex', flexDirection: 'column', textAlign: 'left' }}>
        <span style={{ fontSize: '13px', fontWeight: 600 }}>{name}</span>
        {IconComponent && <span style={{ fontSize: '11px', color: '#444' }}>{effectiveType}</span>}
      </div>

      <div style={{ position: 'absolute', right: -10, top: '40%' }}>
        <PortWidget engine={engine} port={node?.getPort('out')}>
          <div
            style={{
              width: 14,
              height: 14,
              borderRadius: '50%',
              backgroundColor: '#fff',
              border: '1px solid #000',
              cursor: 'pointer'
            }}
          />
        </PortWidget>
      </div>
    </div>
  )
}

HttpNodeWidget.propTypes = {
  node: PropTypes.object,
  engine: PropTypes.object
}

export default HttpNodeWidget
