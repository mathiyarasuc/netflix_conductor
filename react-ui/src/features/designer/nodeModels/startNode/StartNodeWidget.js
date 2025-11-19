// import * as React from 'react'
// import { PortWidget } from '@projectstorm/react-diagrams'
// import PropTypes from 'prop-types'

// export default class StartNodeWidget extends React.Component {
//   render() {
//     return (
//       <div className='srd-circle-node'>
//         <React.Fragment key={this.props.node.id}>
//           <svg width='80' height='80'>
//             <g>
//               <circle
//                 cx='40'
//                 cy='40'
//                 r='30'
//                 fill='white'
//                 stroke={this.props.node.isSelected() ? '#4299e1' : 'rgb(20,20,20)'}
//                 strokeWidth='2px'
//               />
//               <text x='25' y='45'>
//                 Start
//               </text>
//             </g>
//           </svg>
//         </React.Fragment>
//         <div style={{ position: 'absolute', zIndex: 10, left: 58, top: 28 }}>
//           <PortWidget port={this.props.node.getPort('out')} engine={this.props.engine}>
//             <div className='circle-port' />
//           </PortWidget>
//         </div>
//       </div>
//     )
//   }
// }
// StartNodeWidget.propTypes = {
//   node: PropTypes.object,
//   engine: PropTypes.object
// }

import * as React from 'react'
import { PortWidget } from '@projectstorm/react-diagrams'
import PropTypes from 'prop-types'
import { PlayArrow } from '@mui/icons-material'
import { nodeConfig } from 'features/designer/constants/NodeConfig'

export default class StartNodeWidget extends React.Component {
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
            className='custom-node start-node'
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
                backgroundColor: color || '#1565C0',
                borderRadius: '12px',
                width: '36px',
                height: '36px',
                flexShrink: 0
              }}
            >
              <PlayArrow style={{ color: iconColor }} fontSize='small' />
            </div>
            <span style={{ fontSize: '13px', fontWeight: 600 }}>START</span>
          </div>
        </React.Fragment>

        {/* Port widget (connector on right side) */}
        <div style={{ position: 'absolute', left: 113, top: 16 }}>
          <PortWidget port={node.getPort('out')} engine={engine}>
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

StartNodeWidget.propTypes = {
  node: PropTypes.object,
  engine: PropTypes.object
}
