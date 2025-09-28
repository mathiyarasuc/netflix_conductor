import React, { useState, useEffect, useCallback, useRef, useMemo } from 'react'
import PropTypes from 'prop-types'
import { 
  Grid, 
  Typography, 
  TextField, 
  Checkbox, 
  FormControlLabel, 
  Divider, 
  Paper,
  Box,
  Select,
  MenuItem,
  FormControl,
  InputLabel
} from '@mui/material'
import { get, set } from '@totalsoft/react-state-lens'

const ToolParameterForm = ({ schema, inputParametersLens }) => {
  const properties = schema?.properties || {}
  const required = useMemo(() => schema?.required || [], [schema?.required])
  
  // Local state for form values (prevents re-render issues)
  const [localValues, setLocalValues] = useState({})
  const saveTimeoutRef = useRef(null)
  
  // Initialize local values from workflow state ONCE
  useEffect(() => {
    const currentParams = inputParametersLens |> get
    const currentBody = currentParams?.http_request?.body || '{}'
    
    try {
      // Handle both string and object formats properly
      let bodyObject = {}
      
      if (typeof currentBody === 'string') {
        // If it's a JSON string, parse it
        bodyObject = currentBody.trim() ? JSON.parse(currentBody) : {}
      } else if (typeof currentBody === 'object' && currentBody !== null) {
        // If it's already an object, use it directly
        bodyObject = currentBody
      }
      
      setLocalValues(bodyObject)
    } catch (e) {
      console.warn('Failed to parse tool parameters, using empty object:', e)
      setLocalValues({})
    }
  }, [inputParametersLens])
  
  // Debounced save to workflow state - FIXED SERIALIZATION
  const saveToWorkflow = useCallback((values) => {
    if (saveTimeoutRef.current) {
      clearTimeout(saveTimeoutRef.current)
    }
    
    saveTimeoutRef.current = setTimeout(() => {
      const bodyLens = inputParametersLens?.http_request?.body
      if (bodyLens) {
        // Store as proper object for HTTP request body
        // The HTTP layer will handle JSON.stringify() when sending to backend
        set(bodyLens, values)  // Store object, not JSON string
        console.log('Tool parameters saved as object:', values)
      }
    }, 500)
  }, [inputParametersLens])
  
  // UNIVERSAL NESTED VALUE HANDLER
  const handleNestedValueChange = useCallback((fieldPath, value) => {
    const newValues = { ...localValues }
    
    // Parse dot-notation path like "project_context.delivery_method"
    const pathParts = fieldPath.split('.')
    let current = newValues
    
    // Navigate to the parent object
    for (let i = 0; i < pathParts.length - 1; i++) {
      if (!current[pathParts[i]]) {
        current[pathParts[i]] = {}
      }
      current = current[pathParts[i]]
    }
    
    // Set the final value
    current[pathParts[pathParts.length - 1]] = value
    
    setLocalValues(newValues)
    saveToWorkflow(newValues)
  }, [localValues, saveToWorkflow])
  
  // GET NESTED VALUE BY PATH
  const getNestedValue = useCallback((fieldPath) => {
    const pathParts = fieldPath.split('.')
    let current = localValues
    
    for (const part of pathParts) {
      if (current && typeof current === 'object') {
        current = current[part]
      } else {
        return ''
      }
    }
    
    return current || ''
  }, [localValues])
  
  // CREATE STABLE EVENT HANDLERS FOR ANY FIELD TYPE
  const createHandler = useCallback((fieldPath, fieldType) => {
    switch (fieldType) {
      case 'string':
        return (event) => handleNestedValueChange(fieldPath, event.target.value)
      
      case 'integer':
      case 'number':
        return (event) => {
          const numValue = fieldType === 'integer' 
            ? parseInt(event.target.value) || 0
            : parseFloat(event.target.value) || 0
          handleNestedValueChange(fieldPath, numValue)
        }
      
      case 'boolean':
        return (event) => handleNestedValueChange(fieldPath, event.target.checked)
      
      case 'array':
        return (event) => {
          // Handle comma-separated values for simple arrays
          const arrayValue = event.target.value.split(',').map(v => v.trim()).filter(v => v)
          handleNestedValueChange(fieldPath, arrayValue)
        }
      
      default:
        return (event) => handleNestedValueChange(fieldPath, event.target.value)
    }
  }, [handleNestedValueChange])
  
  // RECURSIVE FIELD RENDERER - HANDLES UNLIMITED NESTING
  const renderField = useCallback((fieldName, fieldSchema, fieldPath = '', level = 0) => {
    const fullPath = fieldPath ? `${fieldPath}.${fieldName}` : fieldName
    const isRequired = required.includes(fieldName)
    const fieldType = fieldSchema.type || 'string'
    const description = fieldSchema.description || ''
    const enumValues = fieldSchema.enum || null
    const defaultValue = fieldSchema.default
    
    // Calculate indentation based on nesting level
    const indentLevel = level * 20
    const isNested = level > 0
    
    // HANDLE NESTED OBJECTS RECURSIVELY
    if (fieldType === 'object' && fieldSchema.properties) {
      const nestedProperties = fieldSchema.properties
      
      return (
        <Grid item xs={12} key={fullPath}>
          {/* Nested Object Header */}
          <Paper 
            elevation={level + 1} 
            style={{ 
              padding: '15px', 
              marginLeft: indentLevel,
              marginBottom: '10px',
              background: `rgba(76, 175, 80, ${0.05 + (level * 0.02)})`,
              borderLeft: `4px solid rgba(76, 175, 80, ${0.3 + (level * 0.1)})`
            }}
          >
            <Typography 
              variant={level === 0 ? "subtitle1" : "subtitle2"} 
              style={{ 
                color: '#4caf50', 
                fontWeight: 'bold',
                marginBottom: '10px'
              }}
            >
              {'📦 '.repeat(level + 1)} {fieldName} {isRequired ? '*' : ''}
            </Typography>
            
            {description && (
              <Typography 
                variant="caption" 
                style={{ 
                  color: '#666', 
                  fontStyle: 'italic',
                  display: 'block',
                  marginBottom: '15px'
                }}
              >
                {description}
              </Typography>
            )}
            
            {/* RECURSIVELY RENDER NESTED FIELDS */}
            <Grid container spacing={2}>
              {Object.entries(nestedProperties).map(([nestedFieldName, nestedFieldSchema]) =>
                renderField(nestedFieldName, nestedFieldSchema, fullPath, level + 1)
              )}
            </Grid>
          </Paper>
        </Grid>
      )
    }
    
    // HANDLE ARRAYS
    if (fieldType === 'array') {
      const currentValue = getNestedValue(fullPath)
      const displayValue = Array.isArray(currentValue) ? currentValue.join(', ') : ''
      
      return (
        <Grid item xs={12} md={isNested ? 12 : 6} key={fullPath}>
          <Box style={{ marginLeft: indentLevel }}>
            <TextField
              fullWidth
              label={`📋 ${fieldName}${isRequired ? ' *' : ''} (Array)`}
              value={displayValue}
              onChange={createHandler(fullPath, fieldType)}
              helperText={`${description}${description ? ' - ' : ''}Enter values separated by commas`}
              required={isRequired}
              variant="outlined"
              size="small"
              multiline={displayValue.length > 50}
              rows={displayValue.length > 50 ? 2 : 1}
            />
          </Box>
        </Grid>
      )
    }
    
    // HANDLE ENUM DROPDOWNS
    if (enumValues && enumValues.length > 0) {
      const currentValue = getNestedValue(fullPath) || defaultValue || ''
      
      return (
        <Grid item xs={12} md={isNested ? 12 : 6} key={fullPath}>
          <Box style={{ marginLeft: indentLevel }}>
            <FormControl fullWidth variant="outlined" size="small">
              <InputLabel>{`${fieldName}${isRequired ? ' *' : ''}`}</InputLabel>
              <Select
                value={currentValue}
                onChange={createHandler(fullPath, fieldType)}
                label={`${fieldName}${isRequired ? ' *' : ''}`}
                required={isRequired}
              >
                {enumValues.map(option => (
                  <MenuItem key={option} value={option}>
                    {option}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            {description && (
              <Typography variant="caption" style={{ color: '#666', fontSize: '0.75rem' }}>
                {description}
              </Typography>
            )}
          </Box>
        </Grid>
      )
    }
    
    // HANDLE PRIMITIVE TYPES
    switch (fieldType) {
      case 'string': {
        const currentStringValue = getNestedValue(fullPath) || defaultValue || ''
        return (
          <Grid item xs={12} md={isNested ? 12 : 6} key={fullPath}>
            <Box style={{ marginLeft: indentLevel }}>
              <TextField
                fullWidth
                label={`📝 ${fieldName}${isRequired ? ' *' : ''}`}
                value={currentStringValue}
                onChange={createHandler(fullPath, fieldType)}
                helperText={description}
                required={isRequired}
                variant="outlined"
                size="small"
              />
            </Box>
          </Grid>
        )
      }
        
      case 'integer':
      case 'number': {
        const currentNumValue = getNestedValue(fullPath) || defaultValue || ''
        return (
          <Grid item xs={12} md={isNested ? 12 : 6} key={fullPath}>
            <Box style={{ marginLeft: indentLevel }}>
              <TextField
                fullWidth
                type="number"
                label={`🔢 ${fieldName}${isRequired ? ' *' : ''}`}
                value={currentNumValue}
                onChange={createHandler(fullPath, fieldType)}
                helperText={description}
                required={isRequired}
                variant="outlined"
                size="small"
                inputProps={{
                  step: fieldType === 'integer' ? 1 : 'any'
                }}
              />
            </Box>
          </Grid>
        )
      }
        
      case 'boolean': {
        const currentBoolValue = getNestedValue(fullPath)
        const boolValue = currentBoolValue !== undefined ? currentBoolValue : (defaultValue || false)
        
        return (
          <Grid item xs={12} md={isNested ? 12 : 6} key={fullPath}>
            <Box style={{ marginLeft: indentLevel }}>
              <FormControlLabel
                control={
                  <Checkbox
                    checked={Boolean(boolValue)}
                    onChange={createHandler(fullPath, fieldType)}
                    color="primary"
                  />
                }
                label={`☑️ ${fieldName}${isRequired ? ' *' : ''}`}
              />
              {description && (
                <Typography 
                  variant="caption" 
                  display="block" 
                  style={{ 
                    color: '#666', 
                    marginLeft: '32px',
                    fontSize: '0.75rem'
                  }}
                >
                  {description}
                </Typography>
              )}
            </Box>
          </Grid>
        )
      }
        
      default: {
        // Fallback for unknown types
        const currentDefaultValue = getNestedValue(fullPath) || defaultValue || ''
        return (
          <Grid item xs={12} md={isNested ? 12 : 6} key={fullPath}>
            <Box style={{ marginLeft: indentLevel }}>
              <TextField
                fullWidth
                label={`❓ ${fieldName}${isRequired ? ' *' : ''}`}
                value={currentDefaultValue}
                onChange={createHandler(fullPath, 'string')}
                helperText={`${description} (Type: ${fieldType})`}
                required={isRequired}
                variant="outlined"
                size="small"
              />
            </Box>
          </Grid>
        )
      }
    }
  }, [required, getNestedValue, createHandler])
  
  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (saveTimeoutRef.current) {
        clearTimeout(saveTimeoutRef.current)
      }
    }
  }, [])
  
  if (!properties || Object.keys(properties).length === 0) {
    return (
      <Typography color="textSecondary" style={{ fontStyle: 'italic' }}>
        No parameters required for this tool
      </Typography>
    )
  }
  
  return (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Divider style={{ margin: '10px 0' }} />
        <Typography variant="subtitle2" color="primary" gutterBottom>
          🔧 Tool Parameters ({Object.keys(properties).length} fields)
        </Typography>
      </Grid>
      
      {/* RENDER ALL FIELDS RECURSIVELY */}
      {Object.entries(properties).map(([fieldName, fieldSchema]) =>
        renderField(fieldName, fieldSchema, '', 0)
      )}
      
      <Grid item xs={12}>
        <Divider style={{ margin: '20px 0 10px 0' }} />
        <Typography variant="caption" color="textSecondary">
          ✅ Parameters will be sent as HTTP request body to your tool backend (auto-saved)
        </Typography>
        
        {/* DEBUG: Show current JSON structure */}
        {Object.keys(localValues).length > 0 && (
          <Box style={{ marginTop: '10px' }}>
            <Typography variant="caption" style={{ color: '#4caf50' }}>
              Current Parameters (stored as object):
            </Typography>
            <Paper 
              style={{ 
                padding: '8px', 
                marginTop: '5px', 
                background: '#f5f5f5',
                fontFamily: 'monospace',
                fontSize: '11px',
                maxHeight: '150px',
                overflow: 'auto'
              }}
            >
              {JSON.stringify(localValues, null, 2)}
            </Paper>
          </Box>
        )}
      </Grid>
    </Grid>
  )
}

ToolParameterForm.propTypes = {
  schema: PropTypes.object.isRequired,
  inputParametersLens: PropTypes.object.isRequired
}

export default ToolParameterForm
