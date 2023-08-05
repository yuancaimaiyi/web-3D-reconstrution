import {render, unmountComponentAtNode} from "react-dom";
import {act} from "react-dom/test-utils";
import AuthDialog from "../components/AuthDialog"
import {getByTestId, within} from "@testing-library/react";
import React from "react";

let container = null;

beforeEach(() => {
    container = document.createElement("div");
    document.body.appendChild(container);
});

afterEach(() => {
    unmountComponentAtNode(container);
    container.remove();
    container = null;
});

it("Checks presence of the auth dialog", () => {
    act(() => {
        render(<AuthDialog/>, container);
    });
    expect(within(document.body).getByTestId('auth-dialog-title')).toBeInTheDocument();
    expect(within(document.body).getByTestId('auth-dialog-content')).toBeInTheDocument();
    expect(within(document.body).getByTestId('auth-dialog-ok')).toBeInTheDocument();
});