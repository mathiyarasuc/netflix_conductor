import React from 'react'
import AccountTreeIcon from '@mui/icons-material/AccountTree'
import CodeIcon from '@mui/icons-material/Code'
import BuildIcon from '@mui/icons-material/Build'
import SmartToyIcon from '@mui/icons-material/SmartToy'

const menuConfig = [
  { icon: <BuildIcon />, text: 'NavBar.Tools', name: 'Tools' },           // First (index 0)
  { icon: <SmartToyIcon />, text: 'NavBar.Agents', name: 'Agents' },      // Second (index 1)
  { icon: <AccountTreeIcon />, text: 'NavBar.Workflows', name: 'Workflows' }, // Third (index 2)
  { icon: <CodeIcon />, text: 'NavBar.SystemTasks', name: 'SystemTasks' }     // Last (index 3)
]

export default menuConfig