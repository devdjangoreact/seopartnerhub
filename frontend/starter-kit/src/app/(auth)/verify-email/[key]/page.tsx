'use client'

// React Imports
import { useEffect, useRef, useState } from 'react'

// Next Imports
import Link from 'next/link'
import { useParams, useRouter } from 'next/navigation'

// MUI Imports
import Alert from '@mui/material/Alert'
import Button from '@mui/material/Button'
import CircularProgress from '@mui/material/CircularProgress'
import Typography from '@mui/material/Typography'
import useMediaQuery from '@mui/material/useMediaQuery'
import { styled, useTheme } from '@mui/material/styles'

// Third-party Imports
import classnames from 'classnames'

// Type Imports
import type { SystemMode } from '@core/types'

// Component Imports
import Logo from '@components/layout/shared/Logo'

// Hook Imports
import { useImageVariant } from '@core/hooks/useImageVariant'
import { useSettings } from '@core/hooks/useSettings'

// Auth Imports
import { authClient } from '@/lib/auth/authClient'
import { useAuth } from '@/lib/auth/useAuth'
import { isApiError } from '@/lib/api/apiError'

// Styled Custom Components
const VerifyEmailIllustration = styled('img')(({ theme }) => ({
  zIndex: 2,
  blockSize: 'auto',
  maxBlockSize: 650,
  maxInlineSize: '100%',
  margin: theme.spacing(12),
  [theme.breakpoints.down(1536)]: {
    maxBlockSize: 550
  },
  [theme.breakpoints.down('lg')]: {
    maxBlockSize: 450
  }
}))

const MaskImg = styled('img')({
  blockSize: 'auto',
  maxBlockSize: 355,
  inlineSize: '100%',
  position: 'absolute',
  insetBlockEnd: 0,
  zIndex: -1
})

type VerifyStatus = 'loading' | 'success' | 'expired' | 'error'

const VerifyEmailForm = ({ mode }: { mode: SystemMode }) => {
  // States
  const [status, setStatus] = useState<VerifyStatus>('loading')
  const [errorMessage, setErrorMessage] = useState<string | null>(null)

  // Vars
  const darkImg = '/images/pages/auth-mask-dark.png'
  const lightImg = '/images/pages/auth-mask-light.png'
  const darkIllustration = '/images/illustrations/auth/v2-verify-email-dark.png'
  const lightIllustration = '/images/illustrations/auth/v2-verify-email-light.png'

  // Hooks
  const params = useParams<{ key: string }>()
  const router = useRouter()
  const { applySessionResponse, refresh } = useAuth()
  const { settings } = useSettings()
  const theme = useTheme()
  const hidden = useMediaQuery(theme.breakpoints.down('md'))
  const authBackground = useImageVariant(mode, lightImg, darkImg)
  const characterIllustration = useImageVariant(mode, lightIllustration, darkIllustration)

  // The allauth verification key is single-use: once an email has been
  // verified the second POST with the same key returns
  // `invalid_or_expired_key`. React 19 + Strict Mode (dev) runs effects twice,
  // so without this guard the second call flips the UI from "success" to
  // "expired". Tying the guard to the key keeps it correct if the user opens
  // a different verification link in the same tab.
  const consumedKeyRef = useRef<string | null>(null)

  useEffect(() => {
    const rawKey = typeof params.key === 'string' ? params.key : Array.isArray(params.key) ? params.key[0] : ''
    const key = decodeURIComponent(rawKey)

    if (!key) {
      setStatus('error')
      setErrorMessage('Missing verification key.')

      return
    }

    if (consumedKeyRef.current === key) {
      return
    }

    consumedKeyRef.current = key

    let cancelled = false

    const run = async (): Promise<void> => {
      try {
        const response = await authClient.verifyEmail({ key })

        if (cancelled) {
          return
        }

        applySessionResponse(response)
        await refresh()
        setStatus('success')
      } catch (error) {
        if (cancelled) {
          return
        }

        if (isApiError(error)) {
          if (error.status === 400 || error.status === 410 || error.status === 404) {
            setStatus('expired')
            setErrorMessage(error.message)

            return
          }

          if (error.code === 'network') {
            setStatus('error')
            setErrorMessage('Service unavailable. Please try again.')

            return
          }

          setStatus('error')
          setErrorMessage(error.message)

          return
        }

        setStatus('error')
        setErrorMessage('Verification failed.')
      }
    }

    void run()

    return () => {
      cancelled = true
    }
  }, [params.key, applySessionResponse, refresh])

  return (
    <div className='flex bs-full justify-center'>
      <div
        className={classnames(
          'flex bs-full items-center justify-center flex-1 min-bs-dvh relative p-6 max-md:hidden',
          {
            'border-ie': settings.skin === 'bordered'
          }
        )}
      >
        <VerifyEmailIllustration src={characterIllustration} alt='character-illustration' />
        {!hidden && (
          <MaskImg
            alt='mask'
            src={authBackground}
            className={classnames({ 'scale-x-[-1]': theme.direction === 'rtl' })}
          />
        )}
      </div>
      <div className='flex justify-center items-center bs-full bg-backgroundPaper min-is-full! p-6 md:min-is-[unset]! md:p-12 md:is-[480px]'>
        <Link href='/login' className='absolute block-start-5 sm:block-start-[33px] inline-start-6 sm:start-[38px]'>
          <Logo />
        </Link>
        <div className='flex flex-col gap-6 is-full sm:is-auto md:is-full sm:max-is-[400px] md:max-is-[unset] mbs-11 sm:mbs-14 md:mbs-0'>
          <div className='flex flex-col gap-1'>
            <Typography variant='h4'>Verify your email ✉️</Typography>
            <Typography>We are confirming your verification link with the server.</Typography>
          </div>

          {status === 'loading' && (
            <div className='flex justify-center'>
              <CircularProgress />
            </div>
          )}

          {status === 'success' && (
            <>
              <Alert severity='success'>Your email is verified. You are now signed in.</Alert>
              <Button fullWidth variant='contained' onClick={() => router.push('/home')}>
                Go to dashboard
              </Button>
            </>
          )}

          {status === 'expired' && (
            <>
              <Alert severity='warning'>{errorMessage ?? 'This verification link is no longer valid.'}</Alert>
              <Typography variant='body2' color='text.secondary'>
                Verification links are one-time and expire after a short period. Try registering again or sign in if
                your account is already verified.
              </Typography>
              <div className='flex gap-3'>
                <Button fullWidth component={Link} href='/register' variant='outlined'>
                  Register again
                </Button>
                <Button fullWidth component={Link} href='/login' variant='contained'>
                  Sign in
                </Button>
              </div>
            </>
          )}

          {status === 'error' && (
            <>
              <Alert severity='error'>{errorMessage ?? 'Verification failed.'}</Alert>
              <Button fullWidth component={Link} href='/login' variant='contained'>
                Back to sign in
              </Button>
            </>
          )}
        </div>
      </div>
    </div>
  )
}

const VerifyEmailPage = () => <VerifyEmailForm mode='light' />

export default VerifyEmailPage
