import React from "react";
import { render, unmountComponentAtNode } from "react-dom";
import { act } from "react-dom/test-utils";
import {getByTestId} from "@testing-library/react";
import BoilerplateTab from "../components/BoilerplateTab";
import ReactThreeTestRenderer from "@react-three/test-renderer";

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

test('Checks presence of the boilerplate tab', async () => {
    const renderer = await ReactThreeTestRenderer.create(<BoilerplateTab />)
})