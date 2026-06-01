'use client'

// React Imports
import { useState } from 'react'

// Next Imports
import Link from 'next/link'
import { useParams, useRouter } from 'next/navigation'

// MUI Imports
import Alert from '@mui/material/Alert'
import Button from '@mui/material/Button'
import IconButton from '@mui/material/IconButton'
import InputAdornment from '@mui/material/InputAdornment'
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
  passwordResetConfirmSchema,
  type PasswordResetConfirmValues
} from '@/lib/auth/passwordResetConfirmSchema'
import { authClient } from '@/lib/auth/authClient'
import { useAuth } from '@/lib/auth/useAuth'
import { isApiError } from '@/lib/api/apiError'

// Styled Custom Components
const ResetPasswordIllustration = styled('img')(({ theme }) => ({
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
  maxBlockSize: 330,
  inlineSize: '100%',
  position: 'absolute',
  insetBlockEnd: 0,
  zIndex: -1
})

type FormStatus = 'idle' | 'submitting' | 'success' | 'expired'

const ResetPasswordForm = ({ mode }: { mode: SystemMode }) => {
  // States
  const [isPasswordShown, setIsPasswordShown] = useState(false)
  const [isConfirmPasswordShown, setIsConfirmPasswordShown] = useState(false)
  const [status, setStatus] = useState<FormStatus>('idle')
  const [submitError, setSubmitError] = useState<string | null>(null)

  // Vars
  const darkImg = '/images/pages/auth-mask-dark.png'
  const lightImg = '/images/pages/auth-mask-light.png'
  const darkIllustration = '/images/illustrations/auth/v2-reset-password-dark.png'
  const lightIllustration = '/images/illustrations/auth/v2-reset-password-light.png'

  // Hooks
  const params = useParams<{ key: string }>()
  const router = useRouter()
  const { applySessionResponse, refresh } = useAuth()
  const { settings } = useSettings()
  const theme = useTheme()
  const hidden = useMediaQuery(theme.breakpoints.down('md'))
  const authBackground = useImageVariant(mode, lightImg, darkImg)
  const characterIllustration = useImageVariant(mode, lightIllustration, darkIllustration)

  const rawKey = typeof params.key === 'string' ? params.key : Array.isArray(params.key) ? params.key[0] : ''
  const key = decodeURIComponent(rawKey)

  const {
    control,
    handleSubmit,
    formState: { errors }
  } = useForm<PasswordResetConfirmValues>({
    resolver: zodResolver(passwordResetConfirmSchema),
    defaultValues: { password: '', confirmPassword: '' }
  })

  const handleClickShowPassword = () => setIsPasswordShown(show => !show)
  const handleClickShowConfirmPassword = () => setIsConfirmPasswordShown(show => !show)

  const onSubmit: SubmitHandler<PasswordResetConfirmValues> = async values => {
    if (status === 'submitting') {
      return
    }

    if (!key) {
      setStatus('expired')

      return
    }

    setSubmitError(null)
    setStatus('submitting')

    try {
      const response = await authClient.confirmPasswordReset({ key, password: values.password })

      applySessionResponse(response)
      await refresh()
      setStatus('success')
    } catch (error) {
      if (isApiError(error)) {
        if (error.status === 400 || error.status === 410 || error.status === 404) {
          setStatus('expired')

          return
        }

        if (error.code === 'network') {
          setSubmitError('Service unavailable. Please try again.')
          setStatus('idle')

          return
        }

        setSubmitError(error.message)
        setStatus('idle')

        return
      }

      setSubmitError('Password reset failed. Please request a new link.')
      setStatus('idle')
    }
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
        <ResetPasswordIllustration src={characterIllustration} alt='character-illustration' />
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
            <Typography variant='h4'>Reset Password 🔒</Typography>
            <Typography>Your new password must be different from previously used passwords.</Typography>
          </div>

          {status === 'success' && (
            <>
              <Alert severity='success'>Password updated. You are now signed in.</Alert>
              <Button fullWidth variant='contained' onClick={() => router.push('/home')}>
                Go to dashboard
              </Button>
            </>
          )}

          {status === 'expired' && (
            <>
              <Alert severity='warning'>
                This password reset link has expired or has already been used. Please request a new one.
              </Alert>
              <Button fullWidth component={Link} href='/reset-password' variant='contained'>
                Request new link
              </Button>
            </>
          )}

          {(status === 'idle' || status === 'submitting') && (
            <>
              {submitError !== null && <Alert severity='error'>{submitError}</Alert>}

              <form noValidate autoComplete='off' onSubmit={handleSubmit(onSubmit)} className='flex flex-col gap-6'>
                <Controller
                  name='password'
                  control={control}
                  rules={{ required: true }}
                  render={({ field }) => (
                    <CustomTextField
                      {...field}
                      autoFocus
                      fullWidth
                      label='New Password'
                      placeholder='············'
                      type={isPasswordShown ? 'text' : 'password'}
                      autoComplete='new-password'
                      onChange={event => {
                        field.onChange(event.target.value)
                        setSubmitError(null)
                      }}
                      slotProps={{
                        input: {
                          endAdornment: (
                            <InputAdornment position='end'>
                              <IconButton
                                edge='end'
                                onClick={handleClickShowPassword}
                                onMouseDown={event => event.preventDefault()}
                              >
                                <i className={isPasswordShown ? 'tabler-eye' : 'tabler-eye-off'} />
                              </IconButton>
                            </InputAdornment>
                          )
                        }
                      }}
                      {...(errors.password !== undefined && {
                        error: true,
                        helperText: errors.password.message
                      })}
                    />
                  )}
                />
                <Controller
                  name='confirmPassword'
                  control={control}
                  rules={{ required: true }}
                  render={({ field }) => (
                    <CustomTextField
                      {...field}
                      fullWidth
                      label='Confirm Password'
                      placeholder='············'
                      type={isConfirmPasswordShown ? 'text' : 'password'}
                      autoComplete='new-password'
                      onChange={event => {
                        field.onChange(event.target.value)
                        setSubmitError(null)
                      }}
                      slotProps={{
                        input: {
                          endAdornment: (
                            <InputAdornment position='end'>
                              <IconButton
                                edge='end'
                                onClick={handleClickShowConfirmPassword}
                                onMouseDown={event => event.preventDefault()}
                              >
                                <i className={isConfirmPasswordShown ? 'tabler-eye' : 'tabler-eye-off'} />
                              </IconButton>
                            </InputAdornment>
                          )
                        }
                      }}
                      {...(errors.confirmPassword !== undefined && {
                        error: true,
                        helperText: errors.confirmPassword.message
                      })}
                    />
                  )}
                />
                <Button fullWidth variant='contained' type='submit' disabled={status === 'submitting'}>
                  {status === 'submitting' ? 'Updating…' : 'Set New Password'}
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

const ResetPasswordPage = () => <ResetPasswordForm mode='light' />

export default ResetPasswordPage
