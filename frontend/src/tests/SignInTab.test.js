import React from "react";
import { render, unmountComponentAtNode } from "react-dom";
import { act } from "react-dom/test-utils";
import {getByTestId} from "@testing-library/react";
import SignInTab from "../components/SignInTab";

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

it("Checks presence of the sign in tab", () => {
    act(() => {
        render(<SignInTab />, container);
    });
    expect(getByTestId(container,'sign-in-tab')).toBeInTheDocument();
});