'use client'

// React Imports
import { useState } from 'react'

// Next Imports
import Link from 'next/link'

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
import { registerSchema, type RegisterFormValues } from '@/lib/auth/registerSchema'
import { authClient } from '@/lib/auth/authClient'
import { useAuth } from '@/lib/auth/useAuth'
import { isApiError } from '@/lib/api/apiError'

// Styled Custom Components
const RegisterIllustration = styled('img')(({ theme }) => ({
  zIndex: 2,
  blockSize: 'auto',
  maxBlockSize: 600,
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
  maxBlockSize: 345,
  inlineSize: '100%',
  position: 'absolute',
  insetBlockEnd: 0,
  zIndex: -1
})

type FormStatus = 'idle' | 'submitting' | 'success'

const RegisterForm = ({ mode }: { mode: SystemMode }) => {
  // States
  const [isPasswordShown, setIsPasswordShown] = useState(false)
  const [isConfirmPasswordShown, setIsConfirmPasswordShown] = useState(false)
  const [status, setStatus] = useState<FormStatus>('idle')
  const [submitError, setSubmitError] = useState<string | null>(null)

  // Vars
  const darkImg = '/images/pages/auth-mask-dark.png'
  const lightImg = '/images/pages/auth-mask-light.png'
  const darkIllustration = '/images/illustrations/auth/v2-register-dark.png'
  const lightIllustration = '/images/illustrations/auth/v2-register-light.png'
  const borderedDarkIllustration = '/images/illustrations/auth/v2-register-dark-border.png'
  const borderedLightIllustration = '/images/illustrations/auth/v2-register-light-border.png'

  // Hooks
  const { applySessionResponse } = useAuth()
  const { settings } = useSettings()
  const theme = useTheme()
  const hidden = useMediaQuery(theme.breakpoints.down('md'))
  const authBackground = useImageVariant(mode, lightImg, darkImg)

  const {
    control,
    handleSubmit,
    formState: { errors }
  } = useForm<RegisterFormValues>({
    resolver: zodResolver(registerSchema),
    defaultValues: { email: '', password: '', confirmPassword: '' }
  })

  const characterIllustration = useImageVariant(
    mode,
    lightIllustration,
    darkIllustration,
    borderedLightIllustration,
    borderedDarkIllustration
  )

  const handleClickShowPassword = () => setIsPasswordShown(show => !show)
  const handleClickShowConfirmPassword = () => setIsConfirmPasswordShown(show => !show)

  const onSubmit: SubmitHandler<RegisterFormValues> = async values => {
    if (status === 'submitting') {
      return
    }

    setSubmitError(null)
    setStatus('submitting')

    try {
      const response = await authClient.signup({
        email: values.email.trim(),
        password: values.password
      })

      applySessionResponse(response)
      setStatus('success')
    } catch (error) {
      if (isApiError(error)) {
        if (error.code === 'network') {
          setSubmitError('Service unavailable. Please try again in a moment.')
        } else {
          setSubmitError(error.message)
        }
      } else {
        setSubmitError('Something went wrong. Please try again.')
      }

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
        <RegisterIllustration src={characterIllustration} alt='character-illustration' />
        {!hidden && <MaskImg alt='mask' src={authBackground} />}
      </div>
      <div className='flex justify-center items-center bs-full bg-backgroundPaper min-is-full! p-6 md:min-is-[unset]! md:p-12 md:is-[480px]'>
        <Link href='/login' className='absolute block-start-5 sm:block-start-[33px] inline-start-6 sm:start-[38px]'>
          <Logo />
        </Link>
        <div className='flex flex-col gap-6 is-full sm:is-auto md:is-full sm:max-is-[400px] md:max-is-[unset] mbs-8 sm:mbs-11 md:mbs-0'>
          <div className='flex flex-col gap-1'>
            <Typography variant='h4'>Adventure starts here 🚀</Typography>
            <Typography>Create your SEOPartnerHub account. We will email you a verification link.</Typography>
          </div>

          {status === 'success' ? (
            <>
              <Alert severity='success'>
                Check your inbox — we just sent a verification link to your email. Open it to finish creating your
                account.
              </Alert>
              <Typography variant='body2' color='text.secondary'>
                In local development, emails are captured by Mailpit at{' '}
                <a href='http://localhost:8025'>http://localhost:8025</a>.
              </Typography>
              <div className='flex justify-center items-center flex-wrap gap-2'>
                <Typography>Already verified?</Typography>
                <Typography component={Link} href='/login' color='primary.main'>
                  Sign in instead
                </Typography>
              </div>
            </>
          ) : (
            <>
              {submitError !== null && <Alert severity='error'>{submitError}</Alert>}

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
                      label='Work email'
                      placeholder='Enter your email'
                      autoComplete='email'
                      onChange={event => {
                        field.onChange(event.target.value)
                        setSubmitError(null)
                      }}
                      {...(errors.email !== undefined && {
                        error: true,
                        helperText: errors.email.message
                      })}
                    />
                  )}
                />
                <Controller
                  name='password'
                  control={control}
                  rules={{ required: true }}
                  render={({ field }) => (
                    <CustomTextField
                      {...field}
                      fullWidth
                      label='Password'
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
                      label='Confirm password'
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
                  {status === 'submitting' ? 'Creating account…' : 'Sign Up'}
                </Button>
                <div className='flex justify-center items-center flex-wrap gap-2'>
                  <Typography>Already have an account?</Typography>
                  <Typography component={Link} href='/login' color='primary.main'>
                    Sign in instead
                  </Typography>
                </div>
              </form>
            </>
          )}
        </div>
      </div>
    </div>
  )
}

const RegisterPage = () => <RegisterForm mode='light' />

export default RegisterPage
