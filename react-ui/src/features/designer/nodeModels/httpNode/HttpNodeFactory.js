import * as React from 'react'
import { AbstractReactFactory } from '@projectstorm/react-canvas-core'
import HttpNodeModel from './HttpNodeModel'
import HttpNodeWidget from './HttpNodeWidget'
import { nodeConfig } from 'features/designer/constants/NodeConfig'

export default class HttpNodeFactory extends AbstractReactFactory {
  
  constructor() {
    super(nodeConfig.HTTP.type)
  }

  generateReactWidget(event) {
    return <HttpNodeWidget engine={this.engine} node={event.model} />
  }

  generateModel() {
    return new HttpNodeModel()
  }
}
