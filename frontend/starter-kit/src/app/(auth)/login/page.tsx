'use client'

// React Imports
import { Suspense, useState } from 'react'

// Next Imports
import Link from 'next/link'
import { useRouter, useSearchParams } from 'next/navigation'

// MUI Imports
import Alert from '@mui/material/Alert'
import Button from '@mui/material/Button'
import Checkbox from '@mui/material/Checkbox'
import FormControlLabel from '@mui/material/FormControlLabel'
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

// Config Imports
import themeConfig from '@configs/themeConfig'

// Hook Imports
import { useImageVariant } from '@core/hooks/useImageVariant'
import { useSettings } from '@core/hooks/useSettings'

// Auth Imports
import { loginSchema, type LoginFormValues } from '@/lib/auth/loginSchema'
import { authClient } from '@/lib/auth/authClient'
import { useAuth } from '@/lib/auth/useAuth'
import { isApiError } from '@/lib/api/apiError'
import { NEXT_QUERY_PARAM, resolveSafeRedirect } from '@/lib/auth/requireAuth'

// Styled Custom Components
const LoginIllustration = styled('img')(({ theme }) => ({
  zIndex: 2,
  blockSize: 'auto',
  maxBlockSize: 680,
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

const GENERIC_INVALID_CREDENTIALS = 'Email or password is incorrect.'

type FormStatus = 'idle' | 'submitting'

const LoginForm = ({ mode }: { mode: SystemMode }) => {
  // States
  const [isPasswordShown, setIsPasswordShown] = useState(false)
  const [status, setStatus] = useState<FormStatus>('idle')
  const [submitError, setSubmitError] = useState<string | null>(null)
  const [needsVerification, setNeedsVerification] = useState(false)

  // Vars
  const darkImg = '/images/pages/auth-mask-dark.png'
  const lightImg = '/images/pages/auth-mask-light.png'
  const darkIllustration = '/images/illustrations/auth/v2-login-dark.png'
  const lightIllustration = '/images/illustrations/auth/v2-login-light.png'
  const borderedDarkIllustration = '/images/illustrations/auth/v2-login-dark-border.png'
  const borderedLightIllustration = '/images/illustrations/auth/v2-login-light-border.png'

  // Hooks
  const router = useRouter()
  const searchParams = useSearchParams()
  const { applySessionResponse, refresh } = useAuth()
  const { settings } = useSettings()
  const theme = useTheme()
  const hidden = useMediaQuery(theme.breakpoints.down('md'))
  const authBackground = useImageVariant(mode, lightImg, darkImg)

  const {
    control,
    handleSubmit,
    formState: { errors }
  } = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: { email: '', password: '' }
  })

  const characterIllustration = useImageVariant(
    mode,
    lightIllustration,
    darkIllustration,
    borderedLightIllustration,
    borderedDarkIllustration
  )

  const handleClickShowPassword = () => setIsPasswordShown(show => !show)

  const onSubmit: SubmitHandler<LoginFormValues> = async values => {
    if (status === 'submitting') {
      return
    }

    setSubmitError(null)
    setNeedsVerification(false)
    setStatus('submitting')

    try {
      const response = await authClient.login({
        email: values.email.trim(),
        password: values.password
      })

      applySessionResponse(response)
      await refresh()

      const redirectTo = resolveSafeRedirect(searchParams.get(NEXT_QUERY_PARAM))

      router.push(redirectTo)
    } catch (error) {
      if (isApiError(error)) {
        if (error.code === 'network') {
          setSubmitError('Service unavailable. Please try again in a moment.')
        } else if (error.status === 409) {
          await refresh()
          router.push(resolveSafeRedirect(searchParams.get(NEXT_QUERY_PARAM)))
        } else if (error.status === 429) {
          setSubmitError(error.message)
        } else if (error.fieldErrors.__all__?.some(entry => entry.code === 'email_not_verified')) {
          setNeedsVerification(true)
        } else {
          setSubmitError(GENERIC_INVALID_CREDENTIALS)
        }
      } else {
        setSubmitError(GENERIC_INVALID_CREDENTIALS)
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
        <LoginIllustration src={characterIllustration} alt='character-illustration' />
        {!hidden && <MaskImg alt='mask' src={authBackground} />}
      </div>
      <div className='flex justify-center items-center bs-full bg-backgroundPaper min-is-full! p-6 md:min-is-[unset]! md:p-12 md:is-[480px]'>
        <Link href='/home' className='absolute block-start-5 sm:block-start-[33px] inline-start-6 sm:start-[38px]'>
          <Logo />
        </Link>
        <div className='flex flex-col gap-6 is-full sm:is-auto md:is-full sm:max-is-[400px] md:max-is-[unset] mbs-11 sm:mbs-14 md:mbs-0'>
          <div className='flex flex-col gap-1'>
            <Typography variant='h4'>{`Welcome to ${themeConfig.templateName}! 👋🏻`}</Typography>
            <Typography>Please sign-in to your account and start the adventure</Typography>
          </div>

          {submitError !== null && <Alert severity='error'>{submitError}</Alert>}

          {needsVerification && (
            <Alert severity='warning'>
              Please verify your email before signing in. Check Mailpit at{' '}
              <a href='http://localhost:8025'>http://localhost:8025</a> for the verification link.
            </Alert>
          )}

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
                    setSubmitError(null)
                    setNeedsVerification(false)
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
                  id='login-password'
                  type={isPasswordShown ? 'text' : 'password'}
                  autoComplete='current-password'
                  onChange={event => {
                    field.onChange(event.target.value)
                    setSubmitError(null)
                    setNeedsVerification(false)
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
            <div className='flex justify-between items-center gap-x-3 gap-y-1 flex-wrap'>
              <FormControlLabel control={<Checkbox />} label='Remember me' />
              <Typography className='text-end' color='primary.main' component={Link} href='/reset-password'>
                Forgot password?
              </Typography>
            </div>
            <Button fullWidth variant='contained' type='submit' disabled={status === 'submitting'}>
              {status === 'submitting' ? 'Signing in…' : 'Login'}
            </Button>
            <div className='flex justify-center items-center flex-wrap gap-2'>
              <Typography>New on our platform?</Typography>
              <Typography component={Link} href='/register' color='primary.main'>
                Create an account
              </Typography>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}

const LoginPage = () => (
  <Suspense fallback={null}>
    <LoginForm mode='light' />
  </Suspense>
)

export default LoginPage
