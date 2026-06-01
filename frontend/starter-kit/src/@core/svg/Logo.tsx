// React Imports
import type { SVGAttributes } from 'react'

const Logo = (props: SVGAttributes<SVGElement>) => {
  return (
    <svg width='1em' height='1em' viewBox='0 0 24 24' fill='none' xmlns='http://www.w3.org/2000/svg' {...props}>
      <path
        d='M4.5 5 L12 12 L19.5 5'
        stroke='currentColor'
        strokeWidth='1.75'
        strokeLinecap='round'
        strokeLinejoin='round'
      />
      <path d='M12 12 L12 19.5' stroke='currentColor' strokeWidth='1.75' strokeLinecap='round' />
      <circle cx='4.5' cy='5' r='2.25' fill='currentColor' />
      <circle cx='19.5' cy='5' r='2.25' fill='currentColor' />
      <circle cx='12' cy='19.5' r='2.25' fill='currentColor' />
      <circle cx='12' cy='12' r='3' fill='currentColor' />
    </svg>
  )
}

export default Logo
