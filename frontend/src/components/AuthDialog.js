import React from 'react';
import {Button, Dialog, DialogActions, DialogContent, DialogContentText, DialogTitle} from "@mui/material";

class AuthDialog extends React.Component {
    constructor(props){
        super(props);
    }

    componentWillUnmount() {
        this.setState({isOpen: true});
    }

    renderContent(mode){
        if (mode === 'signin' || mode === 'signup'){
            return (
                <DialogContent data-testid={"auth-dialog-content"}>
                    <DialogContentText id="alert-dialog-description">
                        Check if you are following all of these:
                        <ol>
                            <li>You filled all the fields</li>
                            <li>Your passed a correct e-mail</li>
                            <li>Your password contains at least 8 symbols</li>
                        </ol>
                    </DialogContentText>
                </DialogContent>
            );
        } else if (mode === 'password'){
            return (
                <DialogContent data-testid={"auth-dialog-content"}>
                    <DialogContentText id="alert-dialog-description">
                        Password and confirmed password do not match. Please, try again.
                    </DialogContentText>
                </DialogContent>
            );
        } else {
            return (
                <DialogContent data-testid={"auth-dialog-content"}>
                    <DialogContentText id="alert-dialog-description">
                        {this.props.content ?? "Your user's data is invalid. Please, try again" }
                    </DialogContentText>
                </DialogContent>
            );
        }

    }

    render(){
        return (
            <Dialog
                open={true}
                onClose={this.props.handleClose}
                aria-labelledby="alert-dialog-title"
                aria-describedby="alert-dialog-description"
            >
                <DialogTitle id="alert-dialog-title" data-testid={"auth-dialog-title"}>
                    {"Please, check your input"}
                </DialogTitle>
                {this.renderContent(this.props.mode)}
                <DialogActions>
                    <Button data-testid={"auth-dialog-ok"} onClick={this.props.handleClose}>Ok</Button>
                </DialogActions>
            </Dialog>
        );
    }
}

export default AuthDialog;