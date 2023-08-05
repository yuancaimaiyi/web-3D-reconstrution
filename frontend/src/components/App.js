import React from 'react'
import {BrowserRouter, Route, Routes} from "react-router-dom";
import MainPage from "./MainPage";
import AuthPage from "./AuthPage";
import signInCreator from "../store/actionCreators/signInCreator";
import NotFoundPage from "./NotFoundPage";
import store from "../store/store";
import RequireAuth from "./RequireAuth";
import signOutCreator from "../store/actionCreators/signOutCreator";


class App extends React.Component {
    render(){
        return (
            <BrowserRouter>
                <Routes>
                    <Route path="/" element={<MainPage logout={
                        () => {
                            store.dispatch(signOutCreator());
                        }} display={"info"}/>} />
                    <Route path="/signin" element={<AuthPage login={
                        (value) => {
                            store.dispatch(signInCreator(value));
                        }
                    } mode={'signin'}/>} />
                    <Route path="/signup" element={<AuthPage login={
                        (value) => {
                            store.dispatch(signInCreator(value));
                        }
                    } mode={'signup'}/>} />
                    <Route path="/main/authorized" element={
                        <RequireAuth>
                            <MainPage logout={
                                () => {
                                    store.dispatch(signOutCreator());
                                }
                            } display={"action"}/>
                        </RequireAuth>
                    } />
                    <Route path="/*" element={<NotFoundPage/>} />
                </Routes>
            </BrowserRouter>
        );
    }
}



export default App;