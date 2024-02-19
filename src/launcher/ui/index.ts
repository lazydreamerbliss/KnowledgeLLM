import React from "react";
import { createRoot } from "react-dom/client";
import App from "./App";
import { initRuntime } from "./util/runtimeHelper";

initRuntime();

const container = document.getElementById("app");

const root = createRoot(container!);
root.render(React.createElement(App));
