// Type Imports
import type { ChildrenType } from '@core/types'

// Component Imports
import BlankLayout from '@layouts/BlankLayout'

// Util Imports
import { getSystemMode } from '@core/utils/serverHelpers'

const AuthLayout = async (props: ChildrenType) => {
  const { children } = props
  const systemMode = await getSystemMode()

  return <BlankLayout systemMode={systemMode}>{children}</BlankLayout>
}

export default AuthLayout
