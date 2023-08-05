import React from 'react'
import { Navigate } from "react-router-dom";
import store from "../store/store";

export default class RequireAuth extends React.Component {
    constructor(props){
        super(props);
    }

    render(){
        if (store.getState().username === ''){
            return <Navigate to="/" replace />;
        }
        return this.props.children;
    }
}