export default function authReducer(state, action) {
    switch(action.type) {
        case 'SIGN_IN': return {
            username: action.username,
            email: action.email,
            token: action.token
        };
        case 'SIGN_OUT': return {
            username: '',
            email: '',
            token: ''
        };
        default: return state;
    }
}