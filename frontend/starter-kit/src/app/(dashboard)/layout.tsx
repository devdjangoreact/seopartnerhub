'use client'

import { useEffect, type ReactNode } from 'react'

import { useRouter } from 'next/navigation'

import Box from '@mui/material/Box'
import Button from '@mui/material/Button'
import CircularProgress from '@mui/material/CircularProgress'
import Container from '@mui/material/Container'
import Stack from '@mui/material/Stack'
import Typography from '@mui/material/Typography'

import LayoutWrapper from '@layouts/LayoutWrapper'
import VerticalLayout from '@layouts/VerticalLayout'
import HorizontalLayout from '@layouts/HorizontalLayout'
import Navigation from '@components/layout/vertical/Navigation'
import Navbar from '@components/layout/vertical/Navbar'
import VerticalFooter from '@components/layout/vertical/Footer'
import Header from '@components/layout/horizontal/Header'
import HorizontalFooter from '@components/layout/horizontal/Footer'

import { useAuth } from '@/lib/auth/useAuth'
import { buildLoginRedirect, currentRedirectTarget } from '@/lib/auth/requireAuth'

const DashboardLayout = ({ children }: { children: ReactNode }) => {
  const router = useRouter()
  const { status } = useAuth()

  useEffect(() => {
    if (status === 'unauthenticated') {
      router.replace(buildLoginRedirect(currentRedirectTarget()))
    }
  }, [status, router])

  if (status === 'loading' || status === 'unauthenticated') {
    return (
      <Box display='flex' justifyContent='center' alignItems='center' minHeight='100vh'>
        <CircularProgress />
      </Box>
    )
  }

  if (status === 'error') {
    return (
      <Container maxWidth='sm' sx={{ py: 8 }}>
        <Stack spacing={2}>
          <Typography variant='h5'>Service unavailable</Typography>
          <Typography color='text.secondary'>
            We could not reach the authentication service. Please try again in a moment.
          </Typography>
          <Button variant='contained' onClick={() => router.refresh()}>
            Retry
          </Button>
        </Stack>
      </Container>
    )
  }

  return (
    <LayoutWrapper
      systemMode='light'
      verticalLayout={
        <VerticalLayout navigation={<Navigation mode='light' />} navbar={<Navbar />} footer={<VerticalFooter />}>
          {children}
        </VerticalLayout>
      }
      horizontalLayout={
        <HorizontalLayout header={<Header />} footer={<HorizontalFooter />}>
          {children}
        </HorizontalLayout>
      }
    />
  )
}

export default DashboardLayout
