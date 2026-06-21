import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import { ProofPortal } from "./ProofPortal";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <ProofPortal />
  </StrictMode>,
);
