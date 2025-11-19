import * as React from 'react'
import PropTypes from 'prop-types'
import ForkNode from './ForkNode'
import { PortWidget } from '@projectstorm/react-diagrams'
import '../../styles/classes.css'
import forkNodeStyle from './forkNodeStyle'
import { makeStyles } from '@mui/styles'

const useStyles = makeStyles(forkNodeStyle)

const ForkNodeWidget = ({ engine, node }) => {
  const classes = useStyles()

  return (
    <>
      <ForkNode node={node} />
      <div className={classes.inPort}>
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
      <div className={classes.outPort}>
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
    </>
  )
}

ForkNodeWidget.propTypes = {
  node: PropTypes.object,
  engine: PropTypes.object
}

export default ForkNodeWidget
