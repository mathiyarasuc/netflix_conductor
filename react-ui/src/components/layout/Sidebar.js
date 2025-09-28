import React, { useRef, useCallback } from 'react'
import { useTranslation } from 'react-i18next'
import { useNavigate } from 'react-router-dom'
import PropTypes from 'prop-types'
import { Hidden } from '@mui/material'
import SimpleBar from 'simplebar-react'
import 'simplebar-react/dist/simplebar.min.css'

import { env } from 'utils/env'
import UserMenu from 'components/menu/UserMenu'
import Menu from 'components/menu/Menu'
import { sidebarWrapperHeight } from 'utils/constants'
import { Drawer, SidebarRef, StyledLogo, Typography } from './SidebarStyle'

function SidebarWrapper({ children, drawerOpen }) {
  const sidebarWrapperRef = useRef()
  
  const simpleBarStyle = { height: sidebarWrapperHeight, overflowX: 'hidden' }

  return (
    <SidebarRef ref={sidebarWrapperRef} drawerOpen={drawerOpen}>
      <SimpleBar style={simpleBarStyle}>{children}</SimpleBar>
    </SidebarRef>
  )
}

SidebarWrapper.propTypes = {
  children: PropTypes.array.isRequired,
  drawerOpen: PropTypes.bool.isRequired
}

function Sidebar({ drawerOpen, changeLanguage, closeDrawer, withGradient }) {
  const { i18n, t } = useTranslation()
  const navigate = useNavigate()

  const handleLogoClick = useCallback(() => {
    navigate('/')
  }, [navigate])

  const logoContainerStyle = {
    display: 'flex', 
    alignItems: 'center', 
    cursor: 'pointer',
    textDecoration: 'none',
    padding: '15px 0px 30px 0'
  }

  const logoIconStyle = {
    marginLeft: '22px',
    marginRight: drawerOpen ? '16px' : '18px',
    marginTop: '7px',
    flexShrink: 0,
    width: '30px',
    height: '30px',
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    borderRadius: '50%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    transition: 'all 300ms linear'
  }

  const titleContainerStyle = {
    color: 'white',
    fontFamily: 'Inter, Arial, sans-serif'
  }

  const titleStyle = {
    margin: 0,
    fontSize: '22px',
    fontWeight: 700,
    lineHeight: 1.2,
    color: 'white',
    fontFamily: 'Inter, Arial, sans-serif',
    textShadow: '0 2px 4px rgba(0, 0, 0, 0.5)'
  }

  const subtitleStyle = {
    margin: '8px 0 16px 0',
    fontSize: '14px',
    fontWeight: 500,
    color: 'rgba(255, 255, 255, 0.9)',
    fontStyle: 'italic',
    fontFamily: 'Inter, Arial, sans-serif',
    letterSpacing: '0.5px'
  }

  const brand = (
    <StyledLogo>
      <div onClick={handleLogoClick} style={logoContainerStyle}>
        <div style={logoIconStyle}>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M4 4L20 20" stroke="white" strokeWidth="2" strokeLinecap="round"></path>
            <path d="M20 4L4 20" stroke="white" strokeWidth="2" strokeLinecap="round"></path>
            <path fillRule="evenodd" clipRule="evenodd" d="M12 17C14.7614 17 17 14.7614 17 12C17 9.23858 14.7614 7 12 7C9.23858 7 7 9.23858 7 12C7 14.7614 9.23858 17 12 17ZM12 20C16.4183 20 20 16.4183 20 12C20 7.58172 16.4183 4 12 4C7.58172 4 4 7.58172 4 12C4 16.4183 7.58172 20 12 20Z" fill="white"></path>
          </svg>
        </div>
        
        {drawerOpen && (
          <div className="app-title" style={titleContainerStyle}>
            <h2 style={titleStyle}>
              Artifi Agentic<br />Console
            </h2>
            <p style={subtitleStyle}>
              Commercial Insurance Accelerator
            </p>
          </div>
        )}
      </div>
    </StyledLogo>
  )

  const appVersion = <Typography variant={'caption'}>{`${t('BuildVersion')} ${env.REACT_APP_VERSION}`}</Typography>

  return (
    <div>
      <Hidden mdUp>
        <Drawer
          variant="temporary"
          anchor="right"
          open={drawerOpen}
          onClose={closeDrawer}
          ModalProps={{
            keepMounted: true
          }}
          drawerOpen={drawerOpen}
        >
          {brand}
          <SidebarWrapper drawerOpen={drawerOpen}>
            <UserMenu
              drawerOpen={drawerOpen}
              changeLanguage={changeLanguage}
              language={i18n.language}
              withGradient={withGradient}
            />
            <Menu drawerOpen={drawerOpen} withGradient={withGradient} />
          </SidebarWrapper>
          {appVersion}
        </Drawer>
      </Hidden>
      <Hidden smDown>
        <Drawer anchor="left" variant="permanent" open={drawerOpen} drawerOpen={drawerOpen}>
          {brand}
          <SidebarWrapper drawerOpen={drawerOpen}>
            <UserMenu
              drawerOpen={drawerOpen}
              changeLanguage={changeLanguage}
              language={i18n.language}
              withGradient={withGradient}
            />
            <Menu drawerOpen={drawerOpen} withGradient={withGradient} />
          </SidebarWrapper>
          {appVersion}
        </Drawer>
      </Hidden>
    </div>
  )
}

Sidebar.propTypes = {
  drawerOpen: PropTypes.bool.isRequired,
  closeDrawer: PropTypes.func.isRequired,
  changeLanguage: PropTypes.func.isRequired,
  withGradient: PropTypes.bool.isRequired
}

export default Sidebar