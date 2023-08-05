import React from "react";
import {
    Box,
    Card,
    CardActionArea,
    CardActions,
    CardContent,
    CardMedia,
    Grid,
    IconButton,
    Paper,
    Typography
} from "@mui/material";
import DeleteIcon from "@mui/icons-material/Delete";
import EditIcon from "@mui/icons-material/Edit";

class ImagesDisplay extends React.Component {
    constructor(props) {
        super(props);
    }

    displayImages(images){
        if (images.length > 0){
            let items = [];
            for (let image of images){
                items.push(
                    <Grid key={image.id} item xl={3} md={4} xs={6} >
                        <Card variant={'outlined'} sx={{
                            marginTop: '1em',
                            marginBottom: '1em',
                            marginLeft: '0.5em',
                            marginRight: '0.5em'
                        }}>
                            <CardActionArea>
                                <CardMedia
                                    component="img"
                                    image={image.src}
                                    width={'100%'}
                                    alt={'user photo'}
                                />
                                <CardContent>
                                    <Typography color="text.secondary"> {image.name} </Typography>
                                </CardContent>
                            </CardActionArea>
                            <CardActions >
                                <IconButton  onClick={() => {return this.props.delete(image.id);}}>
                                    <DeleteIcon />
                                </IconButton>
                                <IconButton onClick={() => {return this.props.edit(image.id);}}>
                                    <EditIcon/>
                                </IconButton>

                            </CardActions>
                        </Card>
                    </Grid>

                );
            }
            return (
                <Grid container align-items={'stretch'}>
                    {items}
                </Grid>
            );
        }
        return null;
    }

    render(){
        return (
            <Paper elevation={6}>
                <Box id={'images-panel'}
                     sx={{
                         width: '100%',
                         height: '65vh',
                         overflow: 'auto'
                     }}
                >

                    {this.displayImages(this.props.images)}

                </Box>
            </Paper>
        );
    }
}

export default ImagesDisplay;