const dynamicForkNodeStyle = _theme => {
  const size = 85

  return {
    dynamicFork: {
      position: 'relative',
      width: '120px',
      height: '80px',
      lineHeight: '65px',
      color: 'white',
      textAlign: 'center'
    },
    title: {
      display: 'inline-block',
      verticalAlign: 'middle',
      lineHeight: 'normal'
    },
    inPort: {
      position: 'absolute',
      zIndex: 10,
      left: -9,
      top: size / 2
    },
    outPort: {
      position: 'absolute',
      zIndex: 10,
      left: 105,
      top: size / 2
    }
  }
}

export default dynamicForkNodeStyle
