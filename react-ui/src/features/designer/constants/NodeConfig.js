import DecisionNodeModel from '../nodeModels/decisionNode/DecisionNodeModel'
import EndNodeModel from '../nodeModels/endNode/EndNodeModel'
import LambdaNodeModel from '../nodeModels/lambdaNode/LambdaNodeModel'
import StartNodeModel from '../nodeModels/startNode/StartNodeModel'
import JoinNodeModel from '../nodeModels/joinNode/JoinNodeModel'
import TerminateNodeModel from '../nodeModels/terminateNode/TerminateNodeModel'
import ForkNodeModel from '../nodeModels/forkNode/ForkNodeModel'
import DynamicForkNodeModel from '../nodeModels/dynamicForkNode/DynamicForkNodeModel'
import EventNodeModel from '../nodeModels/eventNode/EventNodeModel'
import HttpNodeModel from '../nodeModels/httpNode/HttpNodeModel'
import { includes } from 'ramda'
import SubworkflowNodeModel from '../nodeModels/subworkflowNode/SubworkflowNodeModel'
import TaskNodeModel from '../nodeModels/taskNode/TaskNodeModel'

const nodeConfigData = {
  START: {
    name: 'START',
    type: 'START',
    color: '#E0F2FE',
    iconColor: '#0D47A1',
    getInstance: () => new StartNodeModel()
  },
  LAMBDA: {
    name: 'LAMBDA',
    type: 'LAMBDA',
    color: '#FFF9C4',
    iconColor: '#FBC02D',
    hasParametersTab: true,
    getInstance: task => new LambdaNodeModel(task)
  },
  EVENT: {
    name: 'EVENT',
    type: 'EVENT',
    color: '#F8BBD0',
    iconColor: '#C2185B',
    hasParametersTab: true,
    getInstance: task => new EventNodeModel(task)
  },
  HTTP: {
    name: 'HTTP',
    type: 'HTTP',
    color: '#FFE0B2',
    iconColor: '#E65100',
    hasParametersTab: true,
    getInstance: task => new HttpNodeModel(task)
  },
  DECISION: {
    name: 'DECISION',
    type: 'DECISION',
    color: '#C8E6C9',
    iconColor: '#2E7D32',
    hasParametersTab: true,
    getInstance: task => new DecisionNodeModel(task)
  },
  TERMINATE: {
    name: 'TERMINATE',
    type: 'TERMINATE',
    color: '#FFCDD2',
    iconColor: '#C62828',
    hasParametersTab: false,
    terminationStatus: {
      completed: 'COMPLETED',
      failed: 'FAILED'
    },
    getInstance: task => new TerminateNodeModel(task)
  },
  JOIN: {
    name: 'JOIN',
    type: 'JOIN',
    color: '#C5CAE9',
    iconColor: '#303F9F',
    hasParametersTab: true,
    getInstance: task => new JoinNodeModel(task)
  },
  FORK_JOIN: {
    name: 'FORK',
    type: 'FORK_JOIN',
    color: '#BBDEFB',
    iconColor: '#1976D2',
    getInstance: task => new ForkNodeModel(task)
  },
  FORK_JOIN_DYNAMIC: {
    name: 'DYNAMIC_FORK',
    type: 'FORK_JOIN_DYNAMIC',
    color: '#E1BEE7',
    iconColor: '#6A1B9A',
    hasParametersTab: true,
    getInstance: task => new DynamicForkNodeModel(task)
  },
  SUB_WORKFLOW: {
    name: 'SUB_WORKFLOW',
    type: 'SUB_WORKFLOW',
    color: '#B3E5FC',
    iconColor: '#0288D1',
    hasParametersTab: true,
    getInstance: task => new SubworkflowNodeModel(task)
  },
  TASK: {
    name: 'TASK',
    type: 'SIMPLE',
    color: '#E8EAF6',
    iconColor: '#3F51B5',
    hasParametersTab: true,
    getInstance: task => new TaskNodeModel(task)
  },
  SIMPLE: {
    name: 'TASK',
    type: 'SIMPLE',
    color: '#E8EAF6',
    iconColor: '#3F51B5',
    hasParametersTab: true,
    getInstance: task => new TaskNodeModel(task)
  },
  DYNAMIC: {
    name: 'TASK',
    type: 'DYNAMIC',
    color: '#E8EAF6',
    iconColor: '#3F51B5',
    hasParametersTab: true,
    getInstance: task => new TaskNodeModel(task)
  },
  END: {
    name: 'END',
    type: 'END',
    color: '#F5F5F5',
    iconColor: '#424242',
    getInstance: () => new EndNodeModel()
  },
  // ✅ ADD THIS NEW ENTRY
  TOOL: {
    name: 'TOOL',
    type: 'HTTP',
    color: '#E8F5E9',
    iconColor: '#2E7D32',
    hasParametersTab: true,
    getInstance: tool => {
      const toolName = tool?.name || tool?.toolName || 'unknown_tool'

      return new HttpNodeModel({
        ...tool,
        type: 'HTTP',
        type1: 'TOOL',
        name: toolName,
        taskReferenceName: tool?.taskReferenceName || `tool_${toolName}_${Date.now()}`,
        inputParameters: {
          http_request: {
            uri: `http://flask-server:7000/tools/${toolName}/execute`,
            method: 'POST',
            accept: 'application/json',
            contentType: 'application/json',
            headers: {},
            body: '${workflow.input}',
            asyncComplete: false,
            connectionTimeOut: 300000,
            readTimeOut: 300000
          }
        }
      })
    }
  },

  AGENT: {
    name: 'AGENT',
    type: 'HTTP', // Agents become HTTP tasks
    color: '#F3E5F5',
    iconColor: '#6A1B9A',
    hasParametersTab: true,
    getInstance: agent => {
      const agentName = agent?.name || agent?.agentName || 'unknown_agent'
      return new HttpNodeModel({
        ...agent,
        type: 'HTTP',
        type1: 'AGENT',
        name: agentName,
        taskReferenceName: agent?.taskReferenceName || `agent_${agentName}_${Date.now()}`,
        inputParameters: {
          http_request: {
            uri: `http://flask-server:7000/agents/${agentName}/execute`, // Your dummy endpoint
            method: 'POST',
            accept: 'application/json',
            contentType: 'application/json',
            headers: {},
            body: '${workflow.input}',
            asyncComplete: false,
            connectionTimeOut: 300000,
            readTimeOut: 300000
          }
        }
      })
    }
  }
}

const handler = {
  get(nodeConfigData, prop, _receiver) {
    return nodeConfigData[prop] ?? nodeConfigData['TASK']
  }
}

export const nodeConfig = new Proxy(nodeConfigData, handler)

export const isDefault = type =>
  includes(type, [
    nodeConfig.LAMBDA.type,
    nodeConfig.TERMINATE.type,
    nodeConfig.EVENT.type,
    nodeConfig.HTTP.type,
    nodeConfig.SUB_WORKFLOW.type,
    nodeConfig.TASK.type
  ])
