import React from "react";
import { render, unmountComponentAtNode } from "react-dom";
import { act } from "react-dom/test-utils";
import {getByTestId} from "@testing-library/react";
import MainNavbar from "../components/MainNavbar";

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

it("Checks presence of the main navbar", () => {
    act(() => {
        render(<MainNavbar />, container);
    });
    expect(getByTestId(container,'main-navbar')).toBeInTheDocument();
});