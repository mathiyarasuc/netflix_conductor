import * as React from 'react'
import { AbstractReactFactory } from '@projectstorm/react-canvas-core'
import TerminateNodeModel from './TerminateNodeModel'
import TerminateNodeWidget from './TerminateNodeWidget'
import { nodeConfig } from 'features/designer/constants/NodeConfig'

export default class TerminateNodeFactory extends AbstractReactFactory {
  constructor() {
    super(nodeConfig.TERMINATE.type)
  }

  generateReactWidget(event) {
    return <TerminateNodeWidget engine={this.engine} node={event.model} />
  }

  generateModel() {
    return new TerminateNodeModel()
  }
}
