import React from 'react'
import PropTypes from 'prop-types'
import { Dialog } from '@totalsoft/rocket-ui'
import CompareDefinition from './CompareDefinition'
import styles from '../styles'
import { makeStyles } from '@mui/styles'

const useStyles = makeStyles(styles)

const CompareDefinitionDialog = ({ open, onClose, definition, currentDefinition }) => {
  const classes = useStyles()

  return (
    <Dialog
      fullWidth={true}
      maxWidth={'xl'}
      id='compareDefinition'
      open={open}
      onClose={onClose}
      className={classes.bodyContent}
      content={<CompareDefinition definition={definition} currentDefinition={currentDefinition} />}
    />
  )
}

CompareDefinitionDialog.propTypes = {
  open: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  definition: PropTypes.object.isRequired,
  currentDefinition: PropTypes.object
}

export default CompareDefinitionDialog