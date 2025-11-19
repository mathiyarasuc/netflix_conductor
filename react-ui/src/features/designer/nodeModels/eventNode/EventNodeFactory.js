import * as React from 'react'
import { AbstractReactFactory } from '@projectstorm/react-canvas-core'
import EventNodeModel from './EventNodeModel'
import EventNodeWidget from './EventNodeWidget'
import { nodeConfig } from 'features/designer/constants/NodeConfig'

export default class EventNodeFactory extends AbstractReactFactory {
  constructor() {
    super(nodeConfig.EVENT.type)
  }

  generateReactWidget(event) {
    return <EventNodeWidget engine={this.engine} node={event.model} />
  }

  generateModel() {
    return new EventNodeModel()
  }
}
