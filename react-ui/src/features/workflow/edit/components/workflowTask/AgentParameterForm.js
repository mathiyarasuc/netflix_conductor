import React, { useState, useEffect, useCallback, useRef, useMemo } from 'react'
import PropTypes from 'prop-types'
import { Grid, Typography, TextField, Box, Paper, IconButton, Button } from '@mui/material'
import { Autocomplete } from '@mui/material'
import EditIcon from '@mui/icons-material/Edit'
import CloseIcon from '@mui/icons-material/Close'
import AddIcon from '@mui/icons-material/Add'
import { get, set } from '@totalsoft/react-state-lens'


const AgentParameterForm = ({ agentName, inputParametersLens, previousNodes }) => {

  const [messages, setMessages] = useState([]) 
  const [threadId] = useState(Math.floor(Math.random() * 100000))

  const [typedValue, setTypedValue] = useState('') 
  const [editingIndex, setEditingIndex] = useState(null)
  const [editingValue, setEditingValue] = useState('')

  const saveTimeoutRef = useRef(null)

  const nodeOptions = useMemo(() => {
    if (!Array.isArray(previousNodes)) return []

    // ✅ System tasks that should use .output only (not .output.response.body)
    const SYSTEM_TASK_TYPES = [
      'LAMBDA', 'EVENT', 'DECISION', 'TERMINATE', 'JOIN',
      'FORK_JOIN', 'FORK_JOIN_DYNAMIC', 'SUB_WORKFLOW',
      'SIMPLE', 'DYNAMIC'
    ]

    return previousNodes.map(node => {
      // ✅ FIXED: Added node?.inputs?. prefix to access nested properties
      const name = node?.inputs?.taskReferenceName || node?.taskReferenceName || node?.name || 'UnnamedNode'
      const nodeType = node?.inputs?.type || node?.type || ''
      const uri = node?.inputs?.inputParameters?.http_request?.uri || node?.inputParameters?.http_request?.uri || ''

      let type = 'other'
      let basePath = '.output.response.body'

      // ✅ FIX: Check if it's a SYSTEM TASK first
      if (SYSTEM_TASK_TYPES.includes(nodeType)) {
        type = 'system'
        basePath = '.output'  // ✅ System tasks only need .output
      } else if (uri.includes('/tools/')) {
        type = 'tool'
        basePath = '.output.response.body.result'
      } else if (uri.includes('/agents/')) {
        type = 'agent'
        basePath = '.output.response.body.response'
      } else if (nodeType === 'HTTP') {
        // Regular HTTP node (not tool/agent)
        type = 'http'
        basePath = '.output.response.body'
      }

      return {
        label: name,
        type,
        basePath
      }
    })
  }, [previousNodes])


  const normalizeValue = useCallback(
    value => {
      if (!value || typeof value !== 'string') return value

      if (value.startsWith('${') && value.endsWith('}')) return value

      const opt = nodeOptions.find(o => value.startsWith(o.label))
      if (!opt) return value

      const suffix = value.slice(opt.label.length)

      return `\${${opt.label}${opt.basePath}${suffix}}`
    },
    [nodeOptions]
  )

const getVisibleLabel = useCallback(
  (value) => {
    if (!value) return "";

    if (!value.startsWith("${") || !value.endsWith("}")) {
      return value;
    }

    let inside = value.substring(2, value.length - 1);

    // ✅ Strip all path suffixes for clean display
    inside = inside.replaceAll(".output.response.body.result", "");  // Tools
    inside = inside.replaceAll(".output.response.body.response", ""); // Agents
    inside = inside.replaceAll(".output.response.body", "");          // Regular HTTP
    // Note: Keep .output for system tasks visible (e.g., "join.output")

    return inside;
  },
  []
);

 useEffect(() => {
  const params = inputParametersLens |> get;
  const body = params?.http_request?.body;

  try {
    let parsed =
      typeof body === "string" ? JSON.parse(body) : body || {};

    let rawValues = [];


    if (Array.isArray(parsed.messages)) {
      rawValues = parsed.messages;
    }


    else if (typeof parsed.messages === "string") {
      rawValues = parsed.messages
        .split(",")
        .map(s => s.trim())
        .filter(Boolean);
    }

    else if (typeof parsed.message === "string") {
      rawValues = parsed.message
        .split(",")
        .map(s => s.trim())
        .filter(Boolean);
    }


    else if (Array.isArray(parsed.message)) {
      rawValues = parsed.message;
    }


    setMessages(rawValues.map(v => normalizeValue(v)));
  } catch (err) {
    console.warn("Invalid workflow body", err);
  }
}, [inputParametersLens, normalizeValue]);


  const saveToWorkflow = useCallback(
    msgArr => {
      if (saveTimeoutRef.current) clearTimeout(saveTimeoutRef.current)

      saveTimeoutRef.current = setTimeout(() => {
        const bodyLens = inputParametersLens?.http_request?.body
        if (bodyLens) {
          // ✅ FIXED: Changed "messages" to "message" (singular) to match backend expectation
          set(bodyLens, {
            thread_id: threadId,
            message: msgArr.join(','),  // ← FIXED: Was "messages", now "message"
            agent_name: agentName
          })
        }
      }, 400)
    },
    [inputParametersLens, agentName, threadId]
  )

  const handleAddClick = useCallback(() => {
    if (!typedValue) return

    const norm = normalizeValue(typedValue)
    const updated = [...messages, norm]

    setMessages(updated)
    saveToWorkflow(updated)
    setTypedValue('') 
  }, [typedValue, messages, normalizeValue, saveToWorkflow])


  const removeHandler = useCallback(
    index =>
      function handler() {
        const updated = messages.filter((_, i) => i !== index)
        setMessages(updated)
        saveToWorkflow(updated)
      },
    [messages, saveToWorkflow]
  )


  const startEdit = useCallback(
    index =>
      function handler() {
        setEditingIndex(index)
        setEditingValue(getVisibleLabel(messages[index]))
      },
    [messages, getVisibleLabel]
  )

  const handleEditChange = useCallback(function (e) {
    setEditingValue(e.target.value)
  }, [])

  const commitEdit = useCallback(() => {
    if (editingIndex == null) return

    const updated = [...messages]
    updated[editingIndex] = normalizeValue(editingValue)

    setMessages(updated)
    saveToWorkflow(updated)

    setEditingIndex(null)
  }, [editingIndex, editingValue, messages, normalizeValue, saveToWorkflow])

  const handleEditKey = useCallback(
    function (e) {
      if (e.key === 'Enter') commitEdit()
      if (e.key === 'Escape') setEditingIndex(null)
    },
    [commitEdit]
  )

  const handleInputChange = useCallback(function handleInputChange(_e, v) {
    setTypedValue(v)
  }, [])

  return (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Typography variant='h6'>{agentName}</Typography>
      </Grid>

      <Grid item xs={12} md={5}>
        <TextField fullWidth disabled label='Thread ID' value={threadId} />
      </Grid>

      <Grid item xs={12} md={6}>
        <Autocomplete
          freeSolo
          fullWidth
          size='medium'
          value={typedValue}
          onInputChange={handleInputChange}
          options={nodeOptions.map(o => o.label)}
          renderInput={renderInput}
        />
      </Grid>
      <Grid item xs={12} md={1}>
        <Button variant='contained' fullWidth color='primary' startIcon={<AddIcon />} sx={{ mt: 1 }} onClick={handleAddClick}>
          Add
        </Button>
      </Grid>

      <Grid item xs={12}>
        <Box
          sx={{
            display: 'flex',
            flexWrap: 'wrap',
            gap: '6px',
            alignItems: 'center'
          }}
        >
          {messages.map((m, i) => {
            const visible = getVisibleLabel(m)
            const editing = editingIndex === i

            return (
              <Box
                key={`msg-${i}`}
                sx={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  background: '#e0f2f1',
                  px: 1,
                  py: 0.5,
                  borderRadius: '16px',
                  maxWidth: '100%',
                  wordBreak: 'break-word' 
                }}
              >
                {editing ? (
                  <TextField
                    size='small'
                    value={editingValue}
                    onChange={handleEditChange}
                    onBlur={commitEdit}
                    onKeyDown={handleEditKey}
                    autoFocus
                  />
                ) : (
                  <>
                    <Typography sx={{ mr: 1 }}>{visible}</Typography>

                    <IconButton size='small' onClick={startEdit(i)}>
                      <EditIcon />
                    </IconButton>

                    <IconButton size='small' onClick={removeHandler(i)}>
                      <CloseIcon />
                    </IconButton>
                  </>
                )}
              </Box>
            )
          })}
        </Box>
      </Grid>

      {/* Debug */}
      <Grid item xs={12}>
        <Typography variant='caption' color='textSecondary'>
          ✅ Parameters will be sent with complete agent record to execution endpoint
        </Typography>
        <Paper
          sx={{
            p: 1,
            fontFamily: 'monospace',
            whiteSpace: 'pre-wrap',
            wordBreak: 'break-word',
            overflow: 'hidden',
            maxHeight: '200px',
            overflowY: 'auto'
          }}
        >
          {JSON.stringify(
            {
              thread_id: threadId,
              message: messages.join(','),
              agent_name: agentName
            },
            null,
            2
          )}
        </Paper>
      </Grid>
    </Grid>
  )
}


function renderInput(params) {
  return <TextField {...params} label='Add Message' size='medium' multiline maxRows={6} />
}

AgentParameterForm.propTypes = {
  agentName: PropTypes.string.isRequired,
  inputParametersLens: PropTypes.object.isRequired,
  previousNodes: PropTypes.array
}

export default AgentParameterForm