import React from 'react'
import {Container} from "@mui/material";
import SignUpTab from "./SignUpTab";
import SignInTab from "./SignInTab";

class AuthPage extends React.Component {
    chooseComponent(mode) {
        if (mode === 'signin') {
            return <SignInTab login={this.props.login}/>;
        }
        return <SignUpTab login={this.props.login}/>;
    }

    render() {
        return (
            <Container maxWidth={'sm'} data-testid={'auth-page'}>
                {this.chooseComponent(this.props.mode)}
            </Container>
        )
    }
}

export default AuthPage;