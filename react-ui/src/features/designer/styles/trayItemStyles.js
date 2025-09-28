import { nodeConfig } from '../constants/NodeConfig'
const trayItemStyles = () => {
  return {
    EVENT: {
      position: 'relative',
      borderRadius: '4px',
      height: '30px',
      width: '30px',
      color: 'white',
      backgroundColor: nodeConfig.EVENT.color,
      lineHeight: '30px',
      textAlign: 'center'
    },
    LAMBDA: {
      position: 'relative',
      borderRadius: '4px',
      height: '30px',
      width: '30px',
      color: 'white',
      backgroundColor: nodeConfig.LAMBDA.color,
      lineHeight: '30px',
      textAlign: 'center'
    },
    HTTP: {
      position: 'relative',
      borderRadius: '4px',
      height: '30px',
      width: '30px',
      color: 'white',
      backgroundColor: nodeConfig.HTTP.color,
      lineHeight: '30px',
      textAlign: 'center'
    },
    JOIN: {
      position: 'relative',
      height: '30px',
      width: '30px',
      color: 'white',
      backgroundColor: nodeConfig.JOIN.color,
      lineHeight: '30px',
      clipPath: 'polygon(0% 0%, 75% 0%, 100% 50%, 75% 100%, 0% 100%)',
      textAlign: 'center'
    },
    FORK_JOIN: {
      position: 'relative',
      height: '30px',
      width: '30px',
      color: 'white',
      backgroundColor: nodeConfig.FORK_JOIN.color,
      lineHeight: '30px',
      clipPath: 'polygon(25% 0%, 100% 1%, 100% 100%, 25% 100%, 0% 50%)',
      textAlign: 'center',
      animation: 'overlay'
    },
    FORK_JOIN_DYNAMIC: {
      position: 'relative',
      height: '30px',
      width: '30px',
      color: 'white',
      backgroundColor: nodeConfig.FORK_JOIN_DYNAMIC.color,
      lineHeight: '30px',
      clipPath: 'polygon(25% 0%, 75% 0%, 100% 50%, 75% 100%, 25% 100%, 0% 50%)',
      textAlign: 'center',
      animation: 'overlay'
    },
    TERMINATE: {
      position: 'relative',
      borderRadius: '4px',
      height: '30px',
      width: '30px',
      color: 'white',
      backgroundColor: nodeConfig.TERMINATE.color,
      lineHeight: '30px',
      textAlign: 'center'
    },
    START: {
      position: 'relative',
      height: '30px',
      width: '30px',
      color: 'white',
      borderRadius: '30px',
      backgroundColor: nodeConfig.START.color,
      lineHeight: '30px',
      textAlign: 'center'
    },
    END: {
      position: 'relative',
      height: '30px',
      width: '30px',
      color: 'white',
      borderRadius: '30px',
      backgroundColor: nodeConfig.END.color,
      lineHeight: '30px',
      textAlign: 'center'
    },
    DECISION: {
      position: 'relative',
      height: '30px',
      width: '30px',
      color: 'white',
      backgroundColor: nodeConfig.DECISION.color,
      lineHeight: '30px',
      clipPath: 'polygon(50% 0%, 100% 50%, 50% 100%, 0% 50%);',
      textAlign: 'center',
      animation: 'overlay'
    },
    TASK: {
      position: 'relative',
      borderRadius: '4px',
      height: '30px',
      width: '30px',
      color: 'white',
      backgroundColor: nodeConfig.TASK.color,
      lineHeight: '30px',
      textAlign: 'center'
    },
    SUB_WORKFLOW: {
      position: 'relative',
      borderRadius: '4px',
      height: '30px',
      width: '30px',
      color: 'white',
      backgroundColor: nodeConfig.SUB_WORKFLOW.color,
      lineHeight: '30px',
      textAlign: 'center'
    },
    // ✅ ADD THIS NEW TOOL STYLE
    TOOL: {
      position: 'relative',
      borderRadius: '4px',
      height: '30px',
      width: '30px',
      color: 'white',
      backgroundColor: 'rgb(76, 175, 80)', // Green color for tools
      lineHeight: '30px',
      textAlign: 'center',
      border: '2px solid #4caf50',
      boxShadow: '0 2px 4px rgba(76, 175, 80, 0.3)'
    },

    // ✅ ADD THIS NEW AGENT STYLE
    AGENT: {
      position: 'relative',
      borderRadius: '4px',
      height: '30px',
      width: '30px',
      color: 'white',
      backgroundColor: 'rgb(156, 39, 176)', // Purple color for agents
      lineHeight: '30px',
      textAlign: 'center',
      border: '2px solid #9c27b0',
      boxShadow: '0 2px 4px rgba(156, 39, 176, 0.3)'
    }
  }
}

export default trayItemStyles
