import Button from '@mui/material/Button'
import Card from '@mui/material/Card'
import CardContent from '@mui/material/CardContent'
import Stack from '@mui/material/Stack'
import Typography from '@mui/material/Typography'

const HomePage = () => {
  return (
    <Stack spacing={6}>
      <Card>
        <CardContent>
          <Stack spacing={3}>
            <Typography variant='h4'>Welcome to SEOPartnerHub</Typography>
            <Typography color='text.secondary'>
              Manage SEO outreach, link-building partnerships, and BizDev workflows from one dashboard.
            </Typography>
            <Stack direction='row' spacing={3} flexWrap='wrap'>
              <Button variant='contained'>View outreach</Button>
              <Button variant='tonal' color='secondary'>
                Open reports
              </Button>
            </Stack>
          </Stack>
        </CardContent>
      </Card>

      <Stack direction={{ xs: 'column', md: 'row' }} spacing={6}>
        <Card className='is-full'>
          <CardContent>
            <Typography variant='h5'>Partnership pipeline</Typography>
            <Typography color='text.secondary'>Track prospects, negotiations, and live placements.</Typography>
          </CardContent>
        </Card>
        <Card className='is-full'>
          <CardContent>
            <Typography variant='h5'>Team activity</Typography>
            <Typography color='text.secondary'>Monitor recent outreach and follow-up actions.</Typography>
          </CardContent>
        </Card>
      </Stack>
    </Stack>
  )
}

export default HomePage
