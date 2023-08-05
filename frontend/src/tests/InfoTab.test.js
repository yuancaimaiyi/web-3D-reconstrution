import React from "react";
import { render, unmountComponentAtNode } from "react-dom";
import { act } from "react-dom/test-utils";
import {getByTestId} from "@testing-library/react";
import InfoTab from "../components/InfoTab";

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

it("Checks presence of the info tab", () => {
    act(() => {
        render(<InfoTab />, container);
    });
    expect(getByTestId(container,'info-tab')).toBeInTheDocument();
});