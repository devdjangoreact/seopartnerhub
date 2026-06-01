'use client'

// React Imports
import { useState } from 'react'

// Next Imports
import Link from 'next/link'

// MUI Imports
import Alert from '@mui/material/Alert'
import Button from '@mui/material/Button'
import Typography from '@mui/material/Typography'
import useMediaQuery from '@mui/material/useMediaQuery'
import { styled, useTheme } from '@mui/material/styles'

// Third-party Imports
import classnames from 'classnames'
import { Controller, useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import type { SubmitHandler } from 'react-hook-form'

// Type Imports
import type { SystemMode } from '@core/types'

// Component Imports
import Logo from '@components/layout/shared/Logo'
import CustomTextField from '@core/components/mui/TextField'

// Hook Imports
import { useImageVariant } from '@core/hooks/useImageVariant'
import { useSettings } from '@core/hooks/useSettings'

// Auth Imports
import {
  passwordResetRequestSchema,
  type PasswordResetRequestValues
} from '@/lib/auth/passwordResetRequestSchema'
import { authClient } from '@/lib/auth/authClient'
import { isApiError } from '@/lib/api/apiError'

// Styled Custom Components
const ForgotPasswordIllustration = styled('img')(({ theme }) => ({
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

const NON_ENUMERATING_MESSAGE =
  'If an account exists for that email, a password reset link is on its way.'

type FormStatus = 'idle' | 'submitting' | 'submitted'

const ForgotPasswordForm = ({ mode }: { mode: SystemMode }) => {
  // States
  const [status, setStatus] = useState<FormStatus>('idle')
  const [systemError, setSystemError] = useState<string | null>(null)

  // Vars
  const darkImg = '/images/pages/auth-mask-dark.png'
  const lightImg = '/images/pages/auth-mask-light.png'
  const darkIllustration = '/images/illustrations/auth/v2-forgot-password-dark.png'
  const lightIllustration = '/images/illustrations/auth/v2-forgot-password-light.png'

  // Hooks
  const { settings } = useSettings()
  const theme = useTheme()
  const hidden = useMediaQuery(theme.breakpoints.down('md'))
  const authBackground = useImageVariant(mode, lightImg, darkImg)
  const characterIllustration = useImageVariant(mode, lightIllustration, darkIllustration)

  const {
    control,
    handleSubmit,
    formState: { errors }
  } = useForm<PasswordResetRequestValues>({
    resolver: zodResolver(passwordResetRequestSchema),
    defaultValues: { email: '' }
  })

  const onSubmit: SubmitHandler<PasswordResetRequestValues> = async values => {
    if (status === 'submitting') {
      return
    }

    setSystemError(null)
    setStatus('submitting')

    try {
      await authClient.requestPasswordReset({ email: values.email.trim() })
    } catch (error) {
      if (isApiError(error) && error.code === 'network') {
        setSystemError('Service unavailable. Please try again in a moment.')
        setStatus('idle')

        return
      }
    }

    setStatus('submitted')
  }

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
        <ForgotPasswordIllustration src={characterIllustration} alt='character-illustration' />
        {!hidden && <MaskImg alt='mask' src={authBackground} />}
      </div>
      <div className='flex justify-center items-center bs-full bg-backgroundPaper min-is-full! p-6 md:min-is-[unset]! md:p-12 md:is-[480px]'>
        <Link href='/login' className='absolute block-start-5 sm:block-start-[33px] inline-start-6 sm:start-[38px]'>
          <Logo />
        </Link>
        <div className='flex flex-col gap-6 is-full sm:is-auto md:is-full sm:max-is-[400px] md:max-is-[unset] mbs-8 sm:mbs-11 md:mbs-0'>
          <div className='flex flex-col gap-1'>
            <Typography variant='h4'>Forgot Password 🔒</Typography>
            <Typography>
              Enter your work email and we&apos;ll send you a reset link if an account exists.
            </Typography>
          </div>

          {status === 'submitted' ? (
            <>
              <Alert severity='info'>{NON_ENUMERATING_MESSAGE}</Alert>
              <Typography variant='body2' color='text.secondary'>
                In local development, emails are captured by Mailpit at{' '}
                <a href='http://localhost:8025'>http://localhost:8025</a>.
              </Typography>
              <Typography className='flex justify-center items-center' color='primary.main'>
                <Link href='/login' className='flex items-center gap-1.5'>
                  <i className='tabler-chevron-left text-xl' />
                  <span>Back to login</span>
                </Link>
              </Typography>
            </>
          ) : (
            <>
              {systemError !== null && <Alert severity='error'>{systemError}</Alert>}

              <form noValidate autoComplete='off' onSubmit={handleSubmit(onSubmit)} className='flex flex-col gap-6'>
                <Controller
                  name='email'
                  control={control}
                  rules={{ required: true }}
                  render={({ field }) => (
                    <CustomTextField
                      {...field}
                      autoFocus
                      fullWidth
                      type='email'
                      label='Email'
                      placeholder='Enter your email'
                      autoComplete='email'
                      onChange={event => {
                        field.onChange(event.target.value)
                        setSystemError(null)
                      }}
                      {...(errors.email !== undefined && {
                        error: true,
                        helperText: errors.email.message
                      })}
                    />
                  )}
                />
                <Button fullWidth variant='contained' type='submit' disabled={status === 'submitting'}>
                  {status === 'submitting' ? 'Sending…' : 'Send Reset Link'}
                </Button>
                <Typography className='flex justify-center items-center' color='primary.main'>
                  <Link href='/login' className='flex items-center gap-1.5'>
                    <i className='tabler-chevron-left text-xl' />
                    <span>Back to login</span>
                  </Link>
                </Typography>
              </form>
            </>
          )}
        </div>
      </div>
    </div>
  )
}

const ForgotPasswordPage = () => <ForgotPasswordForm mode='light' />

export default ForgotPasswordPage
