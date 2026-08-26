import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./styles/base.css";
import "./styles/components.css";
import Landing from "./pages/Landing";

/* Named `landing-entry`, not `landing`, because Windows filenames are
   case-insensitive: a sibling `Landing.tsx` component silently overwrites a
   `landing.tsx` entry, and the build still succeeds -- it just renders an
   empty page. The component now lives in `pages/` for the same reason. */
createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <Landing />
  </StrictMode>,
);
