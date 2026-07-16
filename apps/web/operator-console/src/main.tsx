import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import { ControlCenterApp } from "./App";
import "./styles.css";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <ControlCenterApp />
  </StrictMode>,
);
