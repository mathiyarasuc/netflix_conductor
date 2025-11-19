import React, { useState } from 'react'
import PropTypes from 'prop-types'
import { Box, Typography, TextField, Divider, CircularProgress, IconButton, Collapse, Tooltip } from '@mui/material'
import { PortWidget } from '@projectstorm/react-diagrams'
import SmartToyIcon from '@mui/icons-material/SmartToy'
import ExpandMoreIcon from '@mui/icons-material/ExpandMore'
import ExpandLessIcon from '@mui/icons-material/ExpandLess'
import { nodeConfig } from 'features/designer/constants/NodeConfig'
import { useQuery } from '@apollo/client'
import { AGENT_DETAILS_QUERY } from 'features/workflow/edit/queries/AgentsQuery'

const AgentNodeWidget = ({ node, engine }) => {
  const { color, iconColor } = nodeConfig.AGENT
  const data = node?.inputs || {}

  const agentName = data?.name || node?.options?.name || 'agent_1'

  const [expanded, setExpanded] = useState(false)
  const handleToggleExpand = React.useCallback(() => {
    setExpanded(prev => !prev)
  }, [])

  // ✅ REPLACED: Direct HTTP fetch with GraphQL query
  const { data: agentData, loading, error } = useQuery(AGENT_DETAILS_QUERY, {
    variables: { agentName },
    skip: !agentName, // Don't run query if no agent name
    fetchPolicy: 'cache-first' // Use cache when available
  })

  const agentConfig = agentData?.getAgentDetails || null

  const formData = {
    name: agentConfig?.AgentName || data?.name || agentName || 'Agent',
    description: agentConfig?.AgentDesc || '',
    role: agentConfig?.Configuration?.function_description || '',
    category: agentConfig?.Configuration?.category || 'General',
    instructions: agentConfig?.Configuration?.system_message || ''
  }

  return (
    <Box
      sx={{
        backgroundColor: '#fff',
        border: `1px solid ${iconColor || '#ccc'}`,
        borderRadius: '12px',
        p: 1,
        width: 350,
        position: 'relative',
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        fontFamily: 'Inter, sans-serif',
        transition: 'all 0.3s ease'
      }}
    >
      <Box display='flex' alignItems='center' justifyContent='space-between'>
        <Box display='flex' alignItems='center' gap={1}>
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              backgroundColor: color || '#1565C0',
              borderRadius: '10px',
              width: '36px',
              height: '36px'
            }}
          >
            <SmartToyIcon sx={{ color: iconColor }} />
          </Box>
          <Typography variant='body2' fontWeight={600} noWrap maxWidth='220px'>
            {formData.name}
          </Typography>
        </Box>

        <Tooltip title={expanded ? 'Collapse' : 'Expand'}>
          <IconButton size='small' onClick={handleToggleExpand}>
            {expanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
          </IconButton>
        </Tooltip>
      </Box>

      <Collapse in={expanded} timeout='auto' unmountOnExit >
      <Box p={1.5}>
        <Divider sx={{ borderColor: 'black', borderWidth: '1px', mb: 2 }} />

        {loading ? (
          <Box display='flex' alignItems='center' justifyContent='center' py={4}>
            <CircularProgress size={24} />
            <Typography ml={1}>Loading...</Typography>
          </Box>
        ) : error ? (
          <Typography color='error'>Failed to load: {error.message}</Typography>
        ) : (
          <>
            <Typography fontWeight={600} color='black' variant='body2' mb={0.5}>
              Description
            </Typography>
            <TextField
              fullWidth
              size='small'
              multiline
              minRows={2}
              maxRows={10}
              value={formData.description}
              disabled
              sx={{ mb: 1 }}
              InputProps={{
                sx: {
                  '& textarea': {
                    resize: 'vertical',
                    overflowY: 'auto'
                  }
                }
              }}
            />

            <Typography fontWeight={600} color='black' variant='body2' mb={0.5}>
              Agent Role
            </Typography>
            <TextField fullWidth size='small' value={formData.role} disabled sx={{ mb: 1 }} />

            <Typography fontWeight={600} color='black' variant='body2' mb={0.5}>
              Category
            </Typography>
            <TextField fullWidth size='small' value={formData.category} disabled sx={{ mb: 1 }} />

            <Typography fontWeight={600} color='black' variant='body2' mb={0.5}>
              Instructions
            </Typography>
            <TextField
              fullWidth
              size='small'
              multiline
              minRows={4}
              maxRows={12}
              value={formData.instructions}
              disabled
              sx={{ mb: 1 }}
              InputProps={{
                sx: {
                  '& textarea': {
                    resize: 'vertical',
                    overflowY: 'auto'
                  }
                }
              }}
            />
          </>
        )}
        </Box>
      </Collapse>

      {/* Ports */}
      <div style={{ position: 'absolute', left: -10, top: '50%' }}>
        <PortWidget engine={engine} port={node?.getPort('in')}>
          <div
            style={{
              width: 14,
              height: 14,
              borderRadius: '50%',
              backgroundColor: '#fff',
              border: '1px solid #000'
            }}
          />
        </PortWidget>
      </div>

      <div style={{ position: 'absolute', right: -10, top: '50%' }}>
        <PortWidget engine={engine} port={node?.getPort('out')}>
          <div
            style={{
              width: 14,
              height: 14,
              borderRadius: '50%',
              backgroundColor: '#fff',
              border: '1px solid #000'
            }}
          />
        </PortWidget>
      </div>
    </Box>
  )
}

AgentNodeWidget.propTypes = {
  node: PropTypes.object,
  engine: PropTypes.object
}

export default AgentNodeWidget