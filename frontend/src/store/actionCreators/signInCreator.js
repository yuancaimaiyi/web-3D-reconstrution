export default function signInCreator(value) {
    return {
        type: 'SIGN_IN',
        username: value.username,
        email: value.email,
        token: value.token
    };
}