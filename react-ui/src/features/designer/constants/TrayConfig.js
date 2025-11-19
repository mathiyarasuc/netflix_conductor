import { sysTasksHelpConfig } from 'features/common/Help/constants/TrayHelpConfig'
import { nodeConfig } from './NodeConfig'

const { START, LAMBDA, EVENT, HTTP, DECISION, JOIN, TERMINATE, FORK_JOIN, FORK_JOIN_DYNAMIC, END } = nodeConfig

const trayItems = [
  { type: START.type, name: START.name, color: START.color, isSystemTask: true, helpConfig: sysTasksHelpConfig.START, iconColor: START.iconColor },
  { type: LAMBDA.type, name: LAMBDA.name, color: LAMBDA.color, isSystemTask: true, helpConfig: sysTasksHelpConfig.LAMBDA, iconColor: LAMBDA.iconColor },
  { type: DECISION.type, name: DECISION.name, color: DECISION.color, isSystemTask: true, helpConfig: sysTasksHelpConfig.DECISION,iconColor: DECISION.iconColor },
  { type: EVENT.type, name: EVENT.name, color: EVENT.color, isSystemTask: true, helpConfig: sysTasksHelpConfig.EVENT,iconColor: EVENT.iconColor },
  { type: HTTP.type, name: HTTP.name, color: HTTP.color, isSystemTask: true, helpConfig: sysTasksHelpConfig.HTTP,iconColor: HTTP.iconColor },
  { type: FORK_JOIN.type, name: FORK_JOIN.name, color: FORK_JOIN.color, isSystemTask: true, helpConfig: sysTasksHelpConfig.FORK_JOIN,iconColor: FORK_JOIN.iconColor },
  { type: JOIN.type, name: JOIN.name, color: JOIN.color, isSystemTask: true, helpConfig: sysTasksHelpConfig.JOIN,iconColor: JOIN.iconColor },
  {
    type: FORK_JOIN_DYNAMIC.type,
    name: FORK_JOIN_DYNAMIC.name,
    color: FORK_JOIN_DYNAMIC.color,
    isSystemTask: true,
    helpConfig: sysTasksHelpConfig.FORK_JOIN_DYNAMIC,
    iconColor: FORK_JOIN_DYNAMIC.iconColor
  },
  { type: TERMINATE.type, name: TERMINATE.name, color: TERMINATE.color, isSystemTask: true, helpConfig: sysTasksHelpConfig.TERMINATE,iconColor: TERMINATE.iconColor },
  { type: END.type, name: END.name, color: END.color, isSystemTask: true, helpConfig: sysTasksHelpConfig.END,iconColor: END.iconColor }
]

export default trayItems
