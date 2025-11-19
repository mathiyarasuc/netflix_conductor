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
import { Autocomplete } from '@mui/material'

function makeStringFieldHandlers(stringChangeHandler, description, fieldName, isRequired, nodeOptions = []) {
  let lastSelectedOption = null
  let typingTimeout = null
  let visibleValue = ''

  const handleSelectChange = (_event, newValue) => {
    const matched = nodeOptions.find(opt => opt.value === newValue || opt.label === newValue)

    if (matched) {
      lastSelectedOption = matched
      visibleValue = matched.label
      stringChangeHandler({ target: { value: matched.value } })
    } else {
      visibleValue = newValue || ''
      stringChangeHandler({ target: { value: newValue || '' } })
    }
  }

  const handleInputChange = (_event, newInputValue, reason) => {
    visibleValue = newInputValue || ''

    if (reason === 'clear') {
      lastSelectedOption = null
      stringChangeHandler({ target: { value: '' } })
      return
    }

    if (typingTimeout) clearTimeout(typingTimeout)

    typingTimeout = setTimeout(() => {
      const typed = (newInputValue || '').trim()
      if (!typed) return

      const matchedNode = nodeOptions.find(opt => typed.toLowerCase().startsWith(opt.label.toLowerCase()))

      if (matchedNode) {
        const base = matchedNode.value.replace(/^\$\{|\}$/g, '').trim()
        const label = matchedNode.label
        const suffix = typed.slice(label.length).trim()
        const normalizedSuffix = suffix && !suffix.startsWith('.') && !suffix.startsWith('[') ? `.${suffix}` : suffix

        const formatted = `\${${base}${normalizedSuffix}}`
        stringChangeHandler({ target: { value: formatted } })
      } else {
        stringChangeHandler({ target: { value: typed } })
      }
    }, 400)
  }

  const renderInputField = params => (
    <TextField
      {...params}
      fullWidth
      multiline
      minRows={1}
      maxRows={6}
      label={`${fieldName}${isRequired ? ' *' : ''}`}
      required={isRequired}
      variant='outlined'
      size='small'
      value={visibleValue}
      helperText={description || 'Select or type a value'}
    />
  )

  return { handleSelectChange, handleInputChange, renderInputField }
}

const ToolParameterForm = ({ schema, inputParametersLens, previousNodes }) => {
  const properties = schema?.properties || {}
  const required = useMemo(() => schema?.required || [], [schema?.required])

  // Local state for form values (prevents re-render issues)
  const [localValues, setLocalValues] = useState({})
  const lastSelectedRef = useRef(null)
  const saveTimeoutRef = useRef(null)

  // 🧠 Normalize a plain node name into ${...} template automatically
  function normalizeValueIfNode(value, previousNodes = []) {
    if (!value || typeof value !== 'string') return value
    if (value.startsWith('${')) return value // already normalized

    const matchNode = previousNodes.find(n => n?.taskReferenceName === value || n?.name === value)
    if (!matchNode) return value

    const name = matchNode.taskReferenceName || matchNode.name
    const nodeType = matchNode?.type || ''
    const uri = matchNode?.inputParameters?.http_request?.uri || ''

    // ✅ System tasks that should use .output only
    const SYSTEM_TASK_TYPES = [
      'LAMBDA', 'EVENT', 'DECISION', 'TERMINATE', 'JOIN',
      'FORK_JOIN', 'FORK_JOIN_DYNAMIC', 'SUB_WORKFLOW',
      'SIMPLE', 'DYNAMIC'
    ]

    // ✅ FIX: Check node type first
    if (SYSTEM_TASK_TYPES.includes(nodeType)) {
      return `\${${name}.output}`  // System tasks only need .output
    } else if (uri.includes('/agents/')) {
      return `\${${name}.output.response.body.response}`
    } else if (uri.includes('/tools/')) {
      return `\${${name}.output.response.body.result}`
    } else if (nodeType === 'HTTP') {
      return `\${${name}.output.response.body}`
    } else {
      return `\${${name}.output.response.body}`
    }
  }

  // 🧩 Normalize plain node names in default values when loading
  useEffect(() => {
    if (!previousNodes || previousNodes.length === 0) return

    let updated = null
    Object.keys(localValues).forEach(key => {
      const val = localValues[key]
      if (typeof val === 'string' && !val.startsWith('${')) {
        const normalized = normalizeValueIfNode(val, previousNodes)
        if (normalized !== val) {
          if (!updated) updated = { ...localValues }
          updated[key] = normalized
        }
      }
    })

    if (updated) {
      setLocalValues(updated)
      saveToWorkflow(updated)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [previousNodes])

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
  const saveToWorkflow = useCallback(
    values => {
      if (saveTimeoutRef.current) {
        clearTimeout(saveTimeoutRef.current)
      }

      saveTimeoutRef.current = setTimeout(() => {
        const bodyLens = inputParametersLens?.http_request?.body
        if (bodyLens) {
          // Store as proper object for HTTP request body
          // The HTTP layer will handle JSON.stringify() when sending to backend
          set(bodyLens, values) // Store object, not JSON string
        }
      }, 500)
    },
    [inputParametersLens]
  )

  // UNIVERSAL NESTED VALUE HANDLER
  const handleNestedValueChange = useCallback(
    (fieldPath, value) => {
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
    },
    [localValues, saveToWorkflow]
  )

  // GET NESTED VALUE BY PATH
  const getNestedValue = useCallback(
    fieldPath => {
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
    },
    [localValues]
  )

  // CREATE STABLE EVENT HANDLERS FOR ANY FIELD TYPE
  const createHandler = useCallback(
    (fieldPath, fieldType) => {
      switch (fieldType) {
        case 'string':
          return event => handleNestedValueChange(fieldPath, event.target.value)

        case 'integer':
        case 'number':
          return event => {
            const numValue = fieldType === 'integer' ? parseInt(event.target.value) || 0 : parseFloat(event.target.value) || 0
            handleNestedValueChange(fieldPath, numValue)
          }

        case 'boolean':
          return event => handleNestedValueChange(fieldPath, event.target.checked)

        case 'array':
          return event => {
            // Handle comma-separated values for simple arrays
            const arrayValue = event.target.value
              .split(',')
              .map(v => v.trim())
              .filter(v => v)
            handleNestedValueChange(fieldPath, arrayValue)
          }

        default:
          return event => handleNestedValueChange(fieldPath, event.target.value)
      }
    },
    [handleNestedValueChange]
  )

  // RECURSIVE FIELD RENDERER - HANDLES UNLIMITED NESTING
  const renderField = useCallback(
    (fieldName, fieldSchema, fieldPath = '', level = 0) => {
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
                background: `rgba(76, 175, 80, ${0.05 + level * 0.02})`,
                borderLeft: `4px solid rgba(76, 175, 80, ${0.3 + level * 0.1})`
              }}
            >
              <Typography
                variant={level === 0 ? 'subtitle1' : 'subtitle2'}
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
                  variant='caption'
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
                variant='outlined'
                size='small'
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
              <FormControl fullWidth variant='outlined' size='small'>
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
                <Typography variant='caption' style={{ color: '#666', fontSize: '0.75rem' }}>
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
          let currentStringValue = getNestedValue(fullPath) || defaultValue || ''
          const isSubmissionResponse = fieldName === 'submission_response'
          const isInputField = fieldName === 'input'
          currentStringValue = normalizeValueIfNode(currentStringValue, previousNodes)

          // ✅ System tasks that should use .output only
          const SYSTEM_TASK_TYPES = [
            'LAMBDA', 'EVENT', 'DECISION', 'TERMINATE', 'JOIN',
            'FORK_JOIN', 'FORK_JOIN_DYNAMIC', 'SUB_WORKFLOW',
            'SIMPLE', 'DYNAMIC'
          ]

          const nodeOptions =
            Array.isArray(previousNodes) && previousNodes.length > 0
              ? previousNodes.map(node => {
                  // ✅ FIXED: Added node?.inputs?. prefix to access nested properties
                  const name = node?.inputs?.taskReferenceName || node?.taskReferenceName || node?.name || 'UnnamedNode'
                  const nodeType = node?.inputs?.type || node?.type || ''
                  const uri = node?.inputs?.inputParameters?.http_request?.uri || node?.inputParameters?.http_request?.uri || ''
                  let value

                  // ✅ FIX: Check if it's a SYSTEM TASK first
                  if (SYSTEM_TASK_TYPES.includes(nodeType)) {
                    value = `\${${name}.output}`  // System tasks only need .output
                  } else if (uri.includes('/agents/')) {
                    value = `\${${name}.output.response.body.response}`
                  } else if (uri.includes('/tools/')) {
                    value = `\${${name}.output.response.body.result}`
                  } else if (nodeType === 'HTTP') {
                    value = `\${${name}.output.response.body}`
                  } else {
                    value = `\${${name}.output.response.body}`
                  }

                  return { label: name, value }
                })
              : []

          const matchedOption = nodeOptions.find(opt => {
            const normalizedOpt = opt.value.replace(/^\$\{|\}$/g, '').trim()
            const normalizedCurrent = currentStringValue.replace(/^\$\{|\}$/g, '').trim()
            return normalizedOpt === normalizedCurrent
          })

          const effectiveValue = matchedOption?.value || currentStringValue
          const stringChangeHandler = createHandler(fullPath, fieldType)

          const { handleSelectChange, handleInputChange, renderInputField } = makeStringFieldHandlers(
            stringChangeHandler,
            description,
            fieldName,
            isRequired,
            nodeOptions
          )

          const getVisibleLabel = value => {
            if (!value) return ''
            const match = value.match(/^\$\{([^}]+)\}$/)
            if (match) {
              const base = match[1]
              const parts = base.split('.')
              return parts[0]
            }
            return value
          }

          const visibleValue = getVisibleLabel(currentStringValue)

          const autoCompleteProps = {
            freeSolo: true,
            options: nodeOptions.map(opt => opt.label),
            value: visibleValue,
            onChange: handleSelectChange,
            onInputChange: handleInputChange,
            renderInput: renderInputField
          }

          return (
            <Grid item xs={12} md={isNested ? 12 : 6} key={fullPath}>
              <Box style={{ marginLeft: indentLevel }}>
                {/* ✅ FIX: Show Autocomplete dropdown for ALL fields when previousNodes exist */}
                {nodeOptions.length > 0 ? (
                  <Autocomplete {...autoCompleteProps} />
                ) : (
                  <TextField
                    fullWidth
                    label={`📝 ${fieldName}${isRequired ? ' *' : ''}`}
                    value={currentStringValue}
                    onChange={stringChangeHandler}
                    helperText={description}
                    required={isRequired}
                    variant='outlined'
                    size='small'
                  />
                )}
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
                  type='number'
                  label={`🔢 ${fieldName}${isRequired ? ' *' : ''}`}
                  value={currentNumValue}
                  onChange={createHandler(fullPath, fieldType)}
                  helperText={description}
                  required={isRequired}
                  variant='outlined'
                  size='small'
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
          const boolValue = currentBoolValue !== undefined ? currentBoolValue : defaultValue || false

          return (
            <Grid item xs={12} md={isNested ? 12 : 6} key={fullPath}>
              <Box style={{ marginLeft: indentLevel }}>
                <FormControlLabel
                  control={<Checkbox checked={Boolean(boolValue)} onChange={createHandler(fullPath, fieldType)} color='primary' />}
                  label={`☑️ ${fieldName}${isRequired ? ' *' : ''}`}
                />
                {description && (
                  <Typography
                    variant='caption'
                    display='block'
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
                  label={`${fieldName}${isRequired ? ' *' : ''}`}
                  value={currentDefaultValue}
                  onChange={createHandler(fullPath, 'string')}
                  helperText={`${description} (Type: ${fieldType})`}
                  required={isRequired}
                  variant='outlined'
                  size='small'
                />
              </Box>
            </Grid>
          )
        }
      }
    },
    [required, getNestedValue, createHandler, previousNodes]
  )

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
      <Typography color='textSecondary' style={{ fontStyle: 'italic' }}>
        No parameters required for this tool
      </Typography>
    )
  }

  return (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Divider style={{ margin: '10px 0' }} />
        <Typography variant='subtitle2' color='primary' gutterBottom>
          🔧 Tool Parameters ({Object.keys(properties).length} fields)
        </Typography>
      </Grid>

      {/* RENDER ALL FIELDS RECURSIVELY */}
      {Object.entries(properties).map(([fieldName, fieldSchema]) => renderField(fieldName, fieldSchema, '', 0))}

      <Grid item xs={12}>
        <Divider style={{ margin: '20px 0 10px 0' }} />
        <Typography variant='caption' color='textSecondary'>
          ✅ Parameters will be sent as HTTP request body to your tool backend (auto-saved)
        </Typography>

        {/* DEBUG: Show current JSON structure */}
        {Object.keys(localValues).length > 0 && (
          <Box style={{ marginTop: '10px' }}>
            <Typography variant='caption' style={{ color: '#4caf50' }}>
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
  inputParametersLens: PropTypes.object.isRequired,
  previousNodes: PropTypes.array
}

export default ToolParameterForm