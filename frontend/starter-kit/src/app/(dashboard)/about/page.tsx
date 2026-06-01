import Card from '@mui/material/Card'
import CardContent from '@mui/material/CardContent'
import Stack from '@mui/material/Stack'
import Typography from '@mui/material/Typography'

const AboutPage = () => {
  return (
    <Card>
      <CardContent>
        <Stack spacing={3}>
          <Typography variant='h4'>About SEOPartnerHub</Typography>
          <Typography color='text.secondary'>
            SEOPartnerHub is an internal workspace for SEO and BizDev teams to coordinate outreach,
            partnerships, and performance reporting.
          </Typography>
          <Typography color='text.secondary'>
            The frontend is wired to the local Django authentication API and shares its layout
            primitives with the full SEOPartnerHub frontend.
          </Typography>
        </Stack>
      </CardContent>
    </Card>
  )
}

export default AboutPage
