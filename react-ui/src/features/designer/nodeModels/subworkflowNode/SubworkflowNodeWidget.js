import React from 'react'
import PropTypes from 'prop-types'
import { PortWidget } from '@projectstorm/react-diagrams'
import { nodeConfig } from 'features/designer/constants/NodeConfig'
import WorkflowPresentationDialog from 'features/common/components/modals/WorkflowPresentationDialog'
import SearchIcon from '@mui/icons-material/Search'
import AccountTreeIcon from '@mui/icons-material/AccountTree'

export class SubworkflowNodeWidget extends React.Component {
  state = {
    previewOpen: false
  }

  openPreview = () => this.setState({ previewOpen: true })

  closePreview = () => this.setState({ previewOpen: false })

  render() {
    const { node, engine } = this.props
    
    const { color, iconColor } = nodeConfig.SUB_WORKFLOW
    const { name, subWorkflowParam } = node.inputs

    const style = {
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'flex-start',
      backgroundColor: 'white',
      border: `1px solid ${iconColor || '#ccc'}`,
      borderRadius: '12px',
      padding: '6px 8px',
      position: 'relative',
      minWidth: '150px',
      gap: '8px'
    }

    return (
      <>
        {/* <div className='basic-node' style={style}>
          <div className='node-title'>
            <div className='node-name'>{name}</div>
            <SearchIcon className='preview-icon' style={{ width: '17px', height: '17px' }} onClick={this.openPreview} />
          </div>
          <div className='ports'>
            <div className='in-port'>
              <PortWidget engine={engine} port={node?.getPort('in')}>
                <div className='in' />
              </PortWidget>
              <div className='in-port-name'>{'in'}</div>
            </div>
            <div className='out-port'>
              <div className='out-port-name'>{'out'}</div>
              <PortWidget engine={engine} port={node?.getPort('out')}>
                <div className='out' />
              </PortWidget>
            </div>
          </div>
        </div> */}

        <div className='http-node' style={style}>
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
              backgroundColor: color || '#1565C0',
              borderRadius: '10px',
              width: '36px',
              height: '36px',
              flexShrink: 0
            }}
          >
            <AccountTreeIcon style={{ color: iconColor }} fontSize='small' />
          </div>

          {/* Text Section */}
          <div
            style={{
              display: 'flex',
              flexDirection: 'column',
              flexGrow: 1,
              textAlign: 'left'
            }}
          >
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'flex-start',
                gap: '5px'
              }}
            >
              <span style={{ fontSize: '13px', fontWeight: 600 }}>{name}</span>
              <SearchIcon
                onClick={this.openPreview}
                style={{
                  fontSize: 20,
                  cursor: 'pointer',
                  color: '#666'
                }}
              />
            </div>
            <span style={{ fontSize: '11px', color: '#444' }}>WORKFLOW</span>
          </div>

          {/* Right Port + Search Icon */}
          <div style={{ position: 'absolute', right: -10, top: '40%', display: 'flex', alignItems: 'center', gap: '4px' }}>
            {/* <SearchIcon className='preview-icon' style={{ width: '17px', height: '17px' }} onClick={this.openPreview} /> */}
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
        <WorkflowPresentationDialog
          open={this.state.previewOpen}
          onClose={this.closePreview}
          subworkflowName={subWorkflowParam?.name}
          subworkflowVersion={subWorkflowParam?.version}
        />
      </>
    )
  }
}

SubworkflowNodeWidget.propTypes = {
  node: PropTypes.object,
  engine: PropTypes.object
}

export default SubworkflowNodeWidget
