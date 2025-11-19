import React from 'react'
import PropTypes from 'prop-types'
import { PortWidget } from '@projectstorm/react-diagrams'
import { nodeConfig } from 'features/designer/constants/NodeConfig'
import ShuffleIcon from '@mui/icons-material/Shuffle'

const DecisionNodeWidget = ({ node, engine }) => {
  const config = nodeConfig.DECISION || {}
  const { color, iconColor } = config
  const { name } = node?.inputs || {}

  const style = {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'flex-start',
    backgroundColor: '#fff',
    border: `1px solid ${iconColor || '#ccc'}`,
    borderRadius: '12px',
    padding: '6px 8px',
    position: 'relative',
    minWidth: '150px',
    gap: '8px'
  }

  // ✅ Safely get all output ports (excluding the input)
  const outputPorts = Object.values(node.getPorts?.() || {}).filter(port => !port.options.in)

  return (
    <div className='decision-node' style={style}>
      {/* Left Port (only if exists) */}
      {node.getPort?.('in') && (
        <div style={{ position: 'absolute', left: -10, top: '40%' }}>
          <PortWidget engine={engine} port={node.getPort('in')}>
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
      )}

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
        <ShuffleIcon style={{ color: iconColor }} fontSize='small' />
      </div>

      {/* Text Section */}
      <div style={{ display: 'flex', flexDirection: 'column', textAlign: 'left' }}>
        <span style={{ fontSize: '13px', fontWeight: 600 }}>DECISION</span>
      </div>

      {/* Right Ports (dynamic for cases) */}
      {/* ✅ Centered right-side ports */}
      {outputPorts.map((port, idx) => {
        const totalPorts = outputPorts.length
        const spacing = 28 // distance between ports
        const startOffset = (totalPorts - 1) * spacing * -0.5 // center them vertically

        return (
          <div
            key={port.getID?.() || idx}
            style={{
              position: 'absolute',
              right: -10,
              top: `calc(45% + ${startOffset + idx * spacing}px)`
            }}
          >
            <PortWidget engine={engine} port={port}>
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
        )
      })}
    </div>
  )
}

DecisionNodeWidget.propTypes = {
  node: PropTypes.object.isRequired,
  engine: PropTypes.object.isRequired
}

export default DecisionNodeWidget
