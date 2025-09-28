import React, { useCallback, useState, useEffect } from 'react'
import PropTypes from 'prop-types'
import { Tab, Tabs } from '@mui/material'
import { makeStyles } from '@mui/styles'
import styles from '../styles/sidebarStyles'
import menuConfig from '../constants/DesignerMenuConfig'
import { useTranslation } from 'react-i18next'
import { tasksConfig } from '../constants/TasksConfig'

const useStyles = makeStyles(styles)

const DesignerMenu = ({ setActiveTask }) => {
  const classes = useStyles()
  const { t } = useTranslation()
  const [tabIndex, setTabIndex] = useState(0)

  useEffect(() => {
    setActiveTask(tasksConfig.TOOLS)
  }, [setActiveTask])

  const handleTabChange = useCallback(
    (_event, newValue) => {
      setTabIndex(newValue)
      switch (newValue) {
        case 0:
          setActiveTask(tasksConfig.TOOLS)        // Tools first (default)
          break
        case 1:
          setActiveTask(tasksConfig.AGENTS)       // Agents second  
          break
        case 2:
          setActiveTask(tasksConfig.WORKFLOWS)    // Workflows third
          break
        case 3:
          setActiveTask(tasksConfig.SYSTEM_TASKS) // System_Tasks last
          break
        default:
          break
      }
    },
    [setActiveTask]
  )

  return (
    <>
      <Tabs
        value={tabIndex}
        variant='scrollable'
        scrollButtons='auto'
        allowScrollButtonsMobile
        indicatorColor='secondary'
        textColor='secondary'
        onChange={handleTabChange}
        style={{ margin: '0px 10px 0px 10px' }}
        sx={{
          '& .MuiTabs-flexContainer': {
            gap: 0.5,
          },
          '& .MuiTab-root': {
            minWidth: '70px',
            fontSize: '0.75rem',
            textTransform: 'none',
            padding: '6px 8px',
            '& .MuiSvgIcon-root': {
              fontSize: '1.1rem',
              marginBottom: '2px'
            }
          }
        }}
      >
        {menuConfig?.map((menu, index) => {
          return (
            <Tab
              key={index}
              id={menu.name}
              label={t(menu.text)}
              icon={menu.icon}
              style={{ minWidth: '70px' }}
              classes={{
                root: classes.pills,
                selected: classes.selectedPills
              }}
            />
          )
        })}
      </Tabs>
    </>
  )
}

DesignerMenu.propTypes = {
  setActiveTask: PropTypes.func.isRequired
}

export default DesignerMenu
