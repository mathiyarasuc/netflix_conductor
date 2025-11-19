import * as React from 'react'
import { AbstractReactFactory } from '@projectstorm/react-canvas-core'
import LambdaNodeModel from './LambdaNodeModel'
import LambdaNodeWidget from './LambdaNodeWidget'
import { nodeConfig } from 'features/designer/constants/NodeConfig'

export default class LambdaNodeFactory extends AbstractReactFactory {
  constructor() {
    super(nodeConfig.LAMBDA.type)
  }

  generateReactWidget(event) {
    return <LambdaNodeWidget engine={this.engine} node={event.model} />
  }

  generateModel() {
    return new LambdaNodeModel()
  }
}
