import { createStore } from 'redux';
import authReducer from "./reducers/authReducer";
import initialState from "./initialState";

const saveToLocalStorage = (state) => {
    try {
        sessionStorage.setItem('state', JSON.stringify(state));
    } catch (e) {
        console.error(e);
    }
};

const loadFromLocalStorage = () => {
    try {
        const stateStr = sessionStorage.getItem('state');
        return stateStr ? JSON.parse(stateStr) : undefined;
    } catch (e) {
        console.error(e);
        return undefined;
    }
};

const persistedStore = loadFromLocalStorage() ?? initialState;
const store = createStore(authReducer, persistedStore);

store.subscribe(() => {
    saveToLocalStorage(store.getState());
});

export default store;
