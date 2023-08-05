import React from 'react'
import MainNavbar from "./MainNavbar";
import InfoTab from "./InfoTab";
import BoilerplateTab from "./BoilerplateTab";

class MainPage extends React.Component {

    defineContent(){
        if (this.props.display === 'action'){
            return <BoilerplateTab/>;
        }
        return <InfoTab/>;
    }

    render() {
        return (
            <div data-testid={'main-page'}>
                <MainNavbar logout={this.props.logout} display={this.props.display}/>
                {this.defineContent()}
            </div>)
    }
}

export default MainPage;