import React from 'react'
import {Button, Container, Link, Paper, TextField, Typography} from "@mui/material";
import {Navigate} from "react-router-dom";
import AuthDialog from "./AuthDialog";
import {server} from "../index";

class SignUpTab extends React.Component {
    constructor(props){
        super(props);
        this.state = {
            redirect: false,
            authAlert: false,
            authAlertMode: 'signup',
            login: "",
            password: "",
            email: "",
            confirmedPassword: "",
            token: "",
            error: ""
        };
    }

    componentWillUnmount() {
        this.setState({redirect: false});
    }

    handleLogin = (event) => {
        this.setState({login: event.target.value});
    }

    handlePassword = (event) => {
        this.setState({password: event.target.value});
    }

    handleConfirmedPassword = (event) => {
        this.setState({confirmedPassword: event.target.value});
    }

    handleEmail = (event) => {
        this.setState({email: event.target.value});
    }

    handleDialogClose = () => {
        this.setState({authAlert: false});
        this.setState({authAlertMode: 'signup'});
    }

    enableDialog(value){
        this.setState({authAlert: true});
        this.setState({authAlertMode: value});
    }

    storeLogin = () => {
        this.props.login({
            username: this.state.login,
            email: this.state.email,
            token: this.state.token
        });
    }

    isInputValid = () => {
        return !(this.state.login === "" || this.state.password.length < 8
            || this.state.confirmedPassword.length < 8 || !this.state.email.match(/.+@.+/));
    }

    signUp = () => {
        if (!this.isInputValid()){
            this.enableDialog('signup');
            return;
        }
        if (this.state.password !== this.state.confirmedPassword){
            this.enableDialog('password');
            return;
        }

        let requestUrl = server + 'api/users/';
        let requestData = {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                "user": {
                    username: this.state.login,
                    email: this.state.email,
                    password: this.state.password
                }
            })
        }

        fetch(requestUrl, requestData).then(
            (response) => {
                return response.json();
            }
        ).then((response) => {
            if (response.errors === undefined){
                console.log(response);
                this.setState({token: response.user.token});
                this.storeLogin();
                console.log(this.state);
                this.setState({
                    redirect: true
                });
            } else {
                this.setState({error: response.errors.error});
                this.enableDialog('error');
            }
        }).catch((err) => {
            console.log(err);
        });

    }

    render(){
        return (
            <Paper data-testid={'sign-up-tab'} elevation={6} sx={{
                p: 2,
                minWidth: 300,
                marginTop: 10
            }}>
                <form>
                    <Container>
                        <Typography variant={'h3'} align={'center'}> Sign up </Typography>
                        <Typography align={'center'}> Already have an account? Sign in <Link href={'/signin'}> here </Link> </Typography>
                        <TextField onChange={this.handleLogin} fullWidth label="Login" margin="normal" variant="standard" > </TextField> <br/>
                        <TextField onChange={this.handleEmail} fullWidth label="E-mail" margin="normal" variant="standard" > </TextField> <br/>
                        <TextField onChange={this.handlePassword} fullWidth label="Password" margin="normal" type={'password'} variant="standard" > </TextField> <br/>
                        <TextField onChange={this.handleConfirmedPassword} fullWidth label="Confirm password" margin="normal" type={'password'} variant="standard" > </TextField>
                        <Button onClick={this.signUp} variant="outlined" sx={{marginTop: 1}}> Sign up </Button>
                    </Container>
                </form>
                {
                    this.state.redirect && <Navigate to='/main/authorized' replace={true} />
                }
                {
                    this.state.authAlert && <AuthDialog content={this.state.error} mode={this.state.authAlertMode} handleClose={this.handleDialogClose} />
                }
            </Paper>
        );
    }
}

export default SignUpTab;