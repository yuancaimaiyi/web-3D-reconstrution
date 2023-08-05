import React from 'react';
import { Container, Typography } from '@mui/material';
import backgroundImage from './img_vps_localization.png'; // Replace with the actual path to your image
class InfoTab extends React.Component {
    render() {
        const containerStyle = {
            backgroundImage: `url(${backgroundImage})`,
            backgroundSize: 'cover',
            backgroundRepeat: 'no-repeat',
            backgroundPosition: 'center', // Center the background image
            minHeight: '80vh', // Adjust the height to fill the entire viewport
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
            alignItems: 'center',
            padding: '40px', // Increase padding to give space around the text
            marginTop: '5vh',
        };
        const textStyle = {
            fontFamily: 'Montserrat, Arial, sans-serif',
            fontSize: '40px', // 主标题字体大小增大
            fontWeight: 600,
            color: '#FFFFFF',
            textAlign: 'center',
            textTransform: 'uppercase',
            textShadow: '2px 2px 4px rgba(0, 0, 0, 0.4)',
            marginTop: '20px', // 主标题向上移动一些
        };
        
        const subtitleStyle = {
            fontFamily: 'Montserrat, Arial, sans-serif',
            fontSize: '28px', // 副标题字体大小增大
            fontWeight: 500, // 降低副标题的字重，与主标题有区别
            color: '#FFFFFF',
            textAlign: 'center',
            textShadow: '2px 2px 4px rgba(0, 0, 0, 0.4)', // 为副标题添加阴影效果
            marginBottom: '30px', // 副标题向下移动一些，与主标题有间距
        };
        
        return (
            <Container data-testid={'info-tab'} maxWidth={false} disableGutters style={containerStyle}>
                <Typography variant="h1" component="h1" style={textStyle}>
                   Welcome to the web service for 3D reconstruction!
                </Typography>
                <Typography variant="h4" component="h2" style={subtitleStyle}>
                    VisMap 是一款构建大场景 AR 地图的引擎
                </Typography>
            </Container>
        );
        
    }
}

export default InfoTab;

