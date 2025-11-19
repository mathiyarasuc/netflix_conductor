import React from 'react'
import PropTypes from 'prop-types'
import { PortWidget } from '@projectstorm/react-diagrams'
import { nodeConfig } from 'features/designer/constants/NodeConfig'
import PowerSettingsNewIcon from '@mui/icons-material/PowerSettingsNew' 

export const TerminateNodeWidget = ({ node, engine }) => {
  const { color, iconColor } = nodeConfig.TERMINATE
  const { name } = node.inputs || {}

  const style = {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'flex-start',
    backgroundColor: 'white',
    border: `1px solid ${iconColor || '#ccc'}`,
    borderRadius: '12px',
    padding: '6px 8px',
    position: 'relative',
    minWidth: '140px',
    gap: '8px'
  }

  return (
    <div className='terminate-node' style={style}>
      {/* Left Port */}
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

      {/* Icon Section */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          backgroundColor: color,
          borderRadius: '10px',
          width: '36px',
          height: '36px',
          flexShrink: 0
        }}
      >
        <PowerSettingsNewIcon style={{ color: iconColor }} fontSize='small' />
      </div>

      {/* Text Section */}
      <div style={{ display: 'flex', flexDirection: 'column', textAlign: 'left' }}>
        <span style={{ fontSize: '13px', fontWeight: 600 }}>{'TERMINATE'}</span>
      </div>

      {/* Right Port */}
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

TerminateNodeWidget.propTypes = {
  node: PropTypes.object,
  engine: PropTypes.object
}

export default TerminateNodeWidget
