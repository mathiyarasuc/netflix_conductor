import React, { useState, useEffect, useCallback, useRef } from 'react'
import PropTypes from 'prop-types'
import { Grid, Typography, TextField } from '@mui/material'
import { get, set } from '@totalsoft/react-state-lens'

const AgentParameterForm = ({ agentName, inputParametersLens }) => {
  // Local state for the 2 fixed fields
  const [localValues, setLocalValues] = useState({
    thread_id: Math.floor(Math.random() * 100000), // Auto-generated integer
    message: ''
  })

  const saveTimeoutRef = useRef(null)

  // Initialize from existing workflow state
  useEffect(() => {
    const currentParams = inputParametersLens |> get
    const currentBody = currentParams?.http_request?.body
    
    try {
      let bodyObject = {}
      
      if (typeof currentBody === 'string') {
        bodyObject = currentBody.trim() ? JSON.parse(currentBody) : {}
      } else if (typeof currentBody === 'object' && currentBody !== null) {
        bodyObject = currentBody
      }
      
      if (bodyObject.thread_id || bodyObject.message) {
        setLocalValues({
          thread_id: bodyObject.thread_id || Math.floor(Math.random() * 100000),
          message: bodyObject.message || ''
        })
      }
    } catch (e) {
      // Keep default values
    }
  }, [inputParametersLens])

  // Debounced save to workflow
  const saveToWorkflow = useCallback((values) => {
    if (saveTimeoutRef.current) {
      clearTimeout(saveTimeoutRef.current)
    }

    saveTimeoutRef.current = setTimeout(() => {
      const bodyLens = inputParametersLens?.http_request?.body
      if (bodyLens) {
        // Include complete agent record + user parameters
        const payload = {
          thread_id: values.thread_id,
          message: values.message,
          agent_name: agentName,
          // Note: Complete agent record will be added by backend
        }
        set(bodyLens, payload)
      }
    }, 500)
  }, [inputParametersLens, agentName])

  // Handle message change
  const handleMessageChange = useCallback((event) => {
    const newValues = {
      ...localValues,
      message: event.target.value
    }
    setLocalValues(newValues)
    saveToWorkflow(newValues)
  }, [localValues, saveToWorkflow])

  // Cleanup timeout
  useEffect(() => {
    return () => {
      if (saveTimeoutRef.current) {
        clearTimeout(saveTimeoutRef.current)
      }
    }
  }, [])

  return (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Typography variant="subtitle2" color="primary" gutterBottom>
          Agent: {agentName}
        </Typography>
      </Grid>
      
      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          label="Thread ID"
          value={localValues.thread_id}
          disabled // Read-only field
          variant="outlined"
          size="small"
          helperText="Auto-generated unique identifier"
        />
      </Grid>

      <Grid item xs={12} md={6}>
        <TextField
          fullWidth
          label="Message *"
          value={localValues.message}
          onChange={handleMessageChange}
          variant="outlined"
          size="small"
          required
          helperText="Enter your message for the agent"
          multiline
          rows={2}
        />
      </Grid>

      <Grid item xs={12}>
        <Typography variant="caption" color="textSecondary">
          ✅ Parameters will be sent with complete agent record to execution endpoint
        </Typography>
      </Grid>
    </Grid>
  )
}

AgentParameterForm.propTypes = {
  agentName: PropTypes.string.isRequired,
  inputParametersLens: PropTypes.object.isRequired
}

export default AgentParameterForm
