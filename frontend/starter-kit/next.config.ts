import type { NextConfig } from 'next'

const djangoInternalUrl = process.env.DJANGO_INTERNAL_URL ?? 'http://django:8000'

const nextConfig: NextConfig = {
  basePath: process.env.BASEPATH,
  async rewrites() {
    return [
      { source: '/_allauth/:path*', destination: `${djangoInternalUrl}/_allauth/:path*` },
      { source: '/api/:path*', destination: `${djangoInternalUrl}/api/:path*` }
    ]
  },
  redirects: async () => {
    return [
      {
        source: '/',
        destination: '/home',
        permanent: true,
        locale: false
      }
    ]
  }
}

export default nextConfig
