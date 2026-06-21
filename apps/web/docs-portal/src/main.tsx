import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import { DocsPortal } from "./DocsPortal";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <DocsPortal />
  </StrictMode>,
);
