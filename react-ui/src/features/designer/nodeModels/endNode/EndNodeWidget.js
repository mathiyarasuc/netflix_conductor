import * as React from 'react'
import { PortWidget } from '@projectstorm/react-diagrams'
import PropTypes from 'prop-types'
import { Stop } from '@mui/icons-material'
import { nodeConfig } from 'features/designer/constants/NodeConfig'

export default class EndNodeWidget extends React.Component {
  render() {
    const { node, engine } = this.props
    const type = node?.inputs?.type || ''
    const nodeType = node?.type || type
    const config = nodeConfig[nodeType]
    const { color, iconColor } = config
    return (
      <div className='srd-circle-node'>
        <React.Fragment key={node.id}>
          <div
            className='custom-node end-node'
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'left',
              backgroundColor: '#ffffff',
              border: `1px solid ${iconColor || '#ccc'}`,
              borderRadius: '12px',
              padding: '6px 6px',
              position: 'relative',
              minWidth: '120px',
              gap: '8px'
            }}
          >
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                backgroundColor: color || '#F5F5F5',
                borderRadius: '12px',
                width: '36px',
                height: '36px',
                flexShrink: 0
              }}
            >
              <Stop style={{ color: iconColor }} fontSize='small' />
            </div>
            <span style={{ fontSize: '13px', fontWeight: 600 }}>END</span>
          </div>
        </React.Fragment>

        {/* Port widget (connector on left side) */}
        <div style={{ position: 'absolute', left: -10, top: 16 }}>
          <PortWidget port={node.getPort('in')} engine={engine}>
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
}

EndNodeWidget.propTypes = {
  node: PropTypes.object,
  engine: PropTypes.object
}
