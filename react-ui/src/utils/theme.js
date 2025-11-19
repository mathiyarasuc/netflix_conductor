import { env } from './env'
import { defaultTheme, greenTheme, blueTheme, orangeTheme, redTheme, vividOrangeTheme, lightBlueTheme } from '@totalsoft/rocket-ui'

// Custom Artifi theme based on defaultTheme with blue secondary color
const artifiTheme = {
  ...defaultTheme,
  palette: {
    ...defaultTheme.palette,
    secondary: {
      ...defaultTheme.palette.secondary,
      main: '#1a56db',           // Your exact blue color
      dark: '#3182ce',           // Darker shade for hover states
      light: '#63b3ed',          // Lighter shade for disabled states
      contrastText: '#FFFFFF',   // White text on blue background
      rgba: 'rgba(66, 153, 225, 0.12)'  // Blue with transparency for shadows/highlights
    },
    gradients: {
      ...defaultTheme.palette.gradients,
      secondary: 'linear-gradient(60deg, #1a56db, #1a56db)'  // Blue gradient
    }
  }
}

const getTheme = () => {
  const subDomain = env.REACT_APP_THEME
  switch (subDomain) {
    case 'green':
      return greenTheme
    case 'blue':
      return blueTheme
    case 'orange':
      return orangeTheme
    case 'red':
      return redTheme
    case 'vividOrange':
      return vividOrangeTheme
    case 'lightBlue':
      return lightBlueTheme
    case 'default':
    default:
      return artifiTheme  // Use custom Artifi theme instead of defaultTheme
  }
}

export const theme = getTheme()
export const logo = theme.logo