import StartNodeFactory from './startNode/StartNodeFactory'
import EndNodeFactory from './endNode/EndNodeFactory'
import JoinNodeFactory from './joinNode/JoinNodeFactory'
import ForkNodeFactory from './forkNode/ForkNodeFactory'
import DynamicForkNodeFactory from './dynamicForkNode/DynamicForkNodeFactory'
import SubworkflowNodeFactory from './subworkflowNode/SubworkflowNodeFactory'
import HttpNodeFactory from './httpNode/HttpNodeFactory'
import LambdaNodeFactory from './lambdaNode/LambdaNodeFactory'
import DecisionNodeFactory from './decisionNode/DecisionNodeFactory'
import TerminateNodeFactory from './terminateNode/TerminateNodeFactory'
import EventNodeFactory from './eventNode/EventNodeFactory'
const nodes = [
  StartNodeFactory,
  EndNodeFactory,
  JoinNodeFactory,
  ForkNodeFactory,
  DynamicForkNodeFactory,
  SubworkflowNodeFactory,
  HttpNodeFactory,
  LambdaNodeFactory,
  DecisionNodeFactory,
  TerminateNodeFactory,
  EventNodeFactory
]

export default nodes
