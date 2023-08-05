import React from 'react'
import { Typography } from '@mui/material';

class NotFoundPage extends React.Component {
    render() {
        return <Typography variant="h2" align={'center'} data-testid={'not-found-page'}> Oops! Something went wrong</Typography>
    }
}

export default NotFoundPage;