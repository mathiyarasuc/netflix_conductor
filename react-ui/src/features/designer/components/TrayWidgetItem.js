import React, { useCallback } from 'react'
import styled from '@emotion/styled'
import PropTypes from 'prop-types'
import '../styles/classes.css'
import { Grid } from '@mui/material'
import { makeStyles } from '@mui/styles'
import trayItemStyles from '../styles/trayItemStyles'
import Help from 'features/common/Help/Help'
import PresentationDiagramButton from 'features/common/components/PresentationDiagramButton'
import {
  PlayArrow as PlayArrowIcon,
  Stop as StopIcon,
  Code as CodeIcon,
  Http as HttpIcon,
  DeviceHub as DeviceHubIcon,
  Shuffle as ShuffleIcon,
  ForkRight as ForkRightIcon,
  Hub as HubIcon,
  CallSplit as CallSplitIcon,
  SmartToy as SmartToyIcon,
  Build as BuildIcon,
  AccountTree as AccountTreeIcon
} from '@mui/icons-material'
import PowerSettingsNewIcon from '@mui/icons-material/PowerSettingsNew'

const S = {
  Tray: styled.div`
    width: 100%;
    font-family: 'Inter', Helvetica, Arial, sans-serif;
    font-size: 15px;
    padding: 5px 8px;
    margin-bottom: 5px;
    margin-right: 10px;
    margin-left: 10px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    cursor: pointer;
    background: #ffffff;
    color: #333;
    border-radius: 10px;
    transition: all 0.25s ease;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
    border: 1px solid #e5e7eb;
    &:hover {
      transform: translateY(-3px);
      box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15);
      border-color: #d1d5db;
    }
  `,

  Icon: styled.div`
    width: 36px;
    height: 36px;
    border-radius: 8px;
    background-color: ${({ color }) => color || '#e0e7ff'};
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
    font-size: 16px;
    color: #111827;
    margin-right: 12px;
  `,

  Name: styled.div`
    flex: 1;
    font-size: 16px;
    font-weight: 500;
    letter-spacing: 0.3px;
    overflow-wrap: anywhere;
  `
}

const useStyles = makeStyles(trayItemStyles)

const TrayWidgetItem = ({ item }) => {
  const classes = useStyles()

  const handleOnDragStart = useCallback(
    event => {
      event.dataTransfer.setData('storm-diagram-node', JSON.stringify(item))
    },
    [item]
  )

  const nodeIcons = {
    START: PlayArrowIcon,
    END: StopIcon,
    LAMBDA: CodeIcon,
    HTTP: HttpIcon,
    EVENT: DeviceHubIcon,
    DECISION: ShuffleIcon,
    JOIN: HubIcon,
    FORK_JOIN: ForkRightIcon,
    FORK_JOIN_DYNAMIC: CallSplitIcon,
    SUB_WORKFLOW: AccountTreeIcon,
    TOOL: BuildIcon,
    TASK: BuildIcon,
    SIMPLE: BuildIcon,
    DYNAMIC: BuildIcon,
    AGENT: SmartToyIcon,
    TERMINATE: PowerSettingsNewIcon
  }

  const IconComponent = nodeIcons[item?.type] || BuildIcon // fallback

  return (
    <S.Tray id={item?.name} color={item?.color} draggable={true} onDragStart={handleOnDragStart}>
      {/* <S.Icon color={item?.color}> */}
      {/* {item?.name?.substring(0, 1).toUpperCase()}
       */}
      {/* <div className={classes[`${item?.type}`]}>{item?.name.substring(0, 1).toUpperCase()}</div> */}
      {/* </S.Icon> */}
      <S.Icon color={item?.color}>
        <IconComponent style={{ color: item?.iconColor, fontSize: 20 }} />
      </S.Icon>

      <S.Name>{item?.name}</S.Name>

      {item?.helpConfig && <Help iconSize='small' helpConfig={item?.helpConfig} hasTranslations={true} />}

      {item?.type === 'SUB_WORKFLOW' && item?.name && item?.version && (
        <PresentationDiagramButton subworkflowName={item.name} subworkflowVersion={item.version} iconSize={'small'} />
      )}
    </S.Tray>
  )
}

TrayWidgetItem.propTypes = {
  item: PropTypes.object.isRequired
}

export default TrayWidgetItem
