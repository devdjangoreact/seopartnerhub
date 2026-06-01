'use client'

// Third-party Imports
import classnames from 'classnames'

// Util Imports
import { horizontalLayoutClasses } from '@layouts/utils/layoutClasses'

// Config Imports
import themeConfig from '@configs/themeConfig'

const FooterContent = () => {
  return (
    <div
      className={classnames(horizontalLayoutClasses.footerContent, 'flex items-center justify-between flex-wrap gap-4')}
    >
      <p className='text-textSecondary'>
        {`© ${new Date().getFullYear()} ${themeConfig.templateName}. All rights reserved.`}
      </p>
    </div>
  )
}

export default FooterContent
