import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "@fontsource/inter/400.css";
import "@fontsource/inter/600.css";
import "@fontsource/inter/700.css";
import "@fontsource/merriweather/700.css";
import "@fontsource/merriweather/900.css";
import "./styles.css";
import App from "./App.jsx";

// Keep the browser's install prompt for the "Install app" button (it can fire before React mounts).
addEventListener("beforeinstallprompt", (e) => {
  e.preventDefault();
  window.__pwaPrompt = e;
  dispatchEvent(new Event("pwa-prompt"));
});

// PRD 5.6: refuse to run inside someone else's frame, and only on our own domain (plus local dev).
const ALLOWED = ["lolopodcast.github.io", "localhost", "127.0.0.1"];
if (window.top !== window.self) {
  try { window.top.location.href = window.self.location.href; } catch { document.body.textContent = "This site cannot be embedded."; }
} else if (!ALLOWED.includes(location.hostname)) {
  document.body.textContent = "This site is not authorised on this domain.";
} else {
  createRoot(document.getElementById("root")).render(<StrictMode><App /></StrictMode>);
}
