import React from "react";
import { render, unmountComponentAtNode } from "react-dom";
import { act } from "react-dom/test-utils";
import {getByTestId} from "@testing-library/react";
import MainPage from "../components/MainPage";

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

it("Checks presence of the main page", () => {
    act(() => {
        render(<MainPage display={"info"}/>, container);
    });
    expect(getByTestId(container,'main-page')).toBeInTheDocument();
});