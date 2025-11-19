import * as React from 'react'
import { AbstractReactFactory } from '@projectstorm/react-canvas-core'
import DecisionNodeModel from './DecisionNodeModel'
import DecisionNodeWidget from './DecisionNodeWidget'
import { nodeConfig } from 'features/designer/constants/NodeConfig'

export default class DecisionNodeFactory extends AbstractReactFactory {
  constructor() {
    super(nodeConfig.DECISION.type)
  }

  generateReactWidget(event) {
    return <DecisionNodeWidget engine={this.engine} node={event.model} />
  }

  generateModel() {
    return new DecisionNodeModel()
  }
}
