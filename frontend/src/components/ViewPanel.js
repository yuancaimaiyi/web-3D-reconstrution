import React from 'react'
import {
    Button,
    Container,
    Grid,
    Typography
} from "@mui/material";
import "../styles/ViewPanel.css"
import * as THREE from "three";
import {DDSLoader} from "three-stdlib";
import axios from "axios";
import store from "../store/store";
import mesh from "../texturedMesh.obj"
import colorMap from "../texture_1001.png"
import MeshroomProgress from "./MeshroomProgress";
import CropWindow from "./CropWindow";
import ImagesDisplay from "./ImagesDisplay";
import DbDispatcher from "../database/dbDispatcher";
import {server} from "../index";

THREE.DefaultLoadingManager.addHandler(/\.dds$/i, new DDSLoader());

const recoverFileFromDataURI = (dataURI, name) => {
    let byteString = atob(dataURI.split(',')[1]);

    let mimeString = dataURI.split(',')[0].split(':')[1].split(';')[0];

    let ab = new ArrayBuffer(byteString.length);
    let ia = new Uint8Array(ab);
    for (let i = 0; i < byteString.length; i++) {
        ia[i] = byteString.charCodeAt(i);
    }
    return new File([new Blob([ab], {type: mimeString})], name, {type: mimeString});
}


const defineOffset = (images) => {
    if (!images || images.length === 0){
        return 0;
    }
    let maximum = 0;
    images.forEach((image) => {
        if (+image.id > maximum){
            maximum = +image.id;
        }
    });
    return maximum + 1;
}

class ViewPanel extends React.Component {
    constructor(props){
        super(props);

        this.state = {
            images: [],
            model: mesh,
            texture: colorMap,
            isMeshroomStarted: false,
            progressMessage: "Photos sent to server",
            progressValue: 10,
            isCropOpen: false,
            currentImage: null,
            offset: 0,
            projects: []
        }
        this.statusHandler = null;
        this.dbDispatcher = new DbDispatcher();
    }

    componentDidMount() {
        const restoreImagesURL = (images) => {
            images.forEach((image) => {
                image.src = URL.createObjectURL(image.file);
            });
            return images;
        }

        const interval = 30000;

        this.dbDispatcher.getImages()
            .then((images) => {
                this.setState({
                    images: restoreImagesURL(images),
                    offset: defineOffset(images)
                })
            })
            .catch((err) => {
                console.log(err);
            })

        this.statusHandler = setInterval(() => {
            this.handleStatus();
        }, interval);
        this.handleStatus();
    }

    componentWillUnmount() {
        if (this.statusHandler){
            clearInterval(this.statusHandler);
        }
    }

    handleDelete = (id) => {
        this.dbDispatcher.deleteImage(id);
        this.setState({
           images: this.state.images.filter((item) => {
               return item.id !== id;
           })
        });
    }

    handleCrop = (id) => {
        let image = this.state.images.filter((item) => {
            return item.id === id;
        });

        if (image.length === 0){
            return;
        }

        this.setState({
            isCropOpen: true,
            currentImage: image[0]
        });
    }

    handleCropClose = (newImage) => {
        this.setState({
            isCropOpen: false
        });

        if (!newImage){
            return;
        }
        const updatedFile = new File([newImage], this.state.currentImage.name);
        const updatedCurrentImage = {
            src: URL.createObjectURL(updatedFile),
            file: updatedFile,
            name: this.state.currentImage.name,
            id: this.state.currentImage.id
        }

        this.dbDispatcher.updateImage(updatedCurrentImage);

        let curImages = this.state.images;
        this.setState({
            images: curImages.map((item) => {
                if (item.id !== this.state.currentImage.id){
                    return item;
                }
                return updatedCurrentImage;
            })
        });

        this.setState({
            currentImage: null
        });
    }

    handleUpload = (event) => {
        let files = event.target.files;
        let offset = this.state.offset;

        Object.values(files).forEach((file, idx) => {
            const image = {
                src: URL.createObjectURL(file),
                file: file,
                name: file.name,
                id: offset + idx
            };
            this.dbDispatcher.addImage(image);
            this.setState((prevState) => {
                return {
                    images: prevState.images.concat(image)
                };
            });
        });

        this.setState({
            offset: offset + Object.values(files).length
        })

        document.getElementById("raised-button-file").value = "";
    }

    loadImages = () => {
        const formData = new FormData();
        this.state.images.forEach((image) => {
            formData.append('images', image.file);
        });
        return formData;
    }

    parseStatus = (data) => {
        return data.map((item, idx) => {
            return {
                id: idx,
                datasets: item["Created_at"],
                status: +item["Status"],
                message: item["Comment"],
                downloadURL: item["Download_url"] ?? null,
                removeURL: item['Remove_url'] ?? null,
                isRemovable: !!item['Is_removable']
            }
        })
    }

    handleStatus = () => {
        let requestUrl = server + 'upload/status/';
        const config = {
            headers: {
                'authorization': 'Bearer ' + store.getState().token
            }
        }

        axios.get(requestUrl, config)
            .then((response) => {
                console.log(response);
                this.setState({
                    projects: this.parseStatus(response.data.projects)
                });
            })
            .catch((err) => {
                console.log(err);
            });
    }

    handleStart = () => {
        let requestUrl = server + 'upload/';
        const config = {
            headers: {
                'content-type': 'multipart/form-data',
                'authorization': 'Bearer ' + store.getState().token
            }
        }

        axios.post(requestUrl, this.loadImages(), config)
            .then((response) => {
                console.log(response);
/*
                let obj = new Blob([response.data['obj']] , {type: 'text/plain'});
                let png = recoverFileFromDataURI("data:image/png;base64," + response.data['png'], 'texture.png');

                let objUri = URL.createObjectURL(obj);
                let pngUri = URL.createObjectURL(png);

                console.log(pngUri);

                this.setState({
                    model:  objUri,
                    texture: pngUri
                });*/
            })
            .catch((error) => {
                //this.cancelProgress();
                console.log(error);
            });
    }

    render(){
        return (
            <>
            <Grid data-testid={'view-panel'} container spacing={2}>
                <Grid item xl={6} md={6} xs={12}>
                    <Typography variant={'h4'}> Please, choose your images: </Typography>
                    <input
                        accept="image/*"
                        style={{ display: 'none' }}
                        id="raised-button-file"
                        multiple
                        type="file"
                        onChange={this.handleUpload}
                    />

                    <ImagesDisplay
                        delete={this.handleDelete}
                        edit={this.handleCrop}
                        images={this.state.images}
                    />

                </Grid>
                <Grid item xl={6} md={6} xs={12}>
                    <MeshroomProgress
                        rows={this.state.projects}
                        handleStatus={this.handleStatus}
                    />
                </Grid>
            </Grid>
            <Container data-testid={'control-panel'} maxWidth={'xl'} sx={{
                display: 'flex',
                justifyContent: 'flex-start',
                marginTop: 2,
                marginBottom: 2
            }}>
                <label htmlFor="raised-button-file">
                    <Button variant="raised" component="span" >
                        Upload
                    </Button>
                </label>
                <Button style={{marginLeft: '1em'}} onClick={this.handleStart} > Start </Button>
            </Container>
                <CropWindow
                    isOpen={this.state.isCropOpen}
                    onClose={this.handleCropClose}
                    image={this.state.currentImage?.src}
                />
            </>
        );
    }
}

export default ViewPanel;