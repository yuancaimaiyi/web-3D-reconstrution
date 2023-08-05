import {render, unmountComponentAtNode} from "react-dom";
import {act} from "react-dom/test-utils";
import App from "../components/App";
import {getByTestId} from "@testing-library/react";
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

it("Checks presence of the app", () => {
    act(() => {
        render(<App/>, container);
    });
    expect(getByTestId(container,'main-navbar')).toBeInTheDocument();
    expect(getByTestId(container,'info-tab')).toBeInTheDocument();
});