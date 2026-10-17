import { useEffect, useState } from "react";
import { Icon } from "./components.jsx";

// Chrome / Edge / Android fire `beforeinstallprompt`, possibly before React mounts, so main.jsx
// captures it on window.__pwaPrompt and announces it with a "pwa-prompt" event.
const isStandalone = () => matchMedia("(display-mode: standalone)").matches || navigator.standalone === true;
const isIOS = () => /iphone|ipad|ipod/i.test(navigator.userAgent) || (navigator.platform === "MacIntel" && navigator.maxTouchPoints > 1);

export function useInstall() {
  const [prompt, setPrompt] = useState(() => window.__pwaPrompt || null);
  const [installed, setInstalled] = useState(isStandalone);
  useEffect(() => {
    const onPrompt = () => setPrompt(window.__pwaPrompt);
    const onInstalled = () => { setInstalled(true); setPrompt(null); };
    addEventListener("pwa-prompt", onPrompt);
    addEventListener("appinstalled", onInstalled);
    return () => { removeEventListener("pwa-prompt", onPrompt); removeEventListener("appinstalled", onInstalled); };
  }, []);
  const mode = installed ? null : prompt ? "prompt" : isIOS() ? "ios" : null;
  const install = async () => {
    if (!prompt) return;
    prompt.prompt();
    await prompt.userChoice.catch(() => null);
    window.__pwaPrompt = null;
    setPrompt(null);
  };
  return { mode, install };
}

function ShareIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" style={{ display: "inline", verticalAlign: "-3px" }}>
      <path d="M12 3v12M8 7l4-4 4 4M5 11v9h14v-9" />
    </svg>
  );
}

export function IOSHelp({ t, onClose }) {
  useEffect(() => {
    const esc = (e) => e.key === "Escape" && onClose();
    addEventListener("keydown", esc);
    return () => removeEventListener("keydown", esc);
  }, [onClose]);
  return (
    <div className="modal-back" role="presentation" onClick={onClose}>
      <div className="modal card" role="dialog" aria-modal="true" aria-labelledby="ios-title" onClick={(e) => e.stopPropagation()}>
        <h2 id="ios-title" className="h2">{t("install_ios_title")}</h2>
        <ol className="install-steps">
          <li>{t("install_ios_1a")} <ShareIcon /> {t("install_ios_1b")}</li>
          <li>{t("install_ios_2")}</li>
          <li>{t("install_ios_3")}</li>
        </ol>
        <p className="mini">{t("install_ios_note")}</p>
        <button className="btn solid self-end" onClick={onClose} autoFocus>{t("close")}</button>
      </div>
    </div>
  );
}

export function InstallButton({ t, mode, install, onIOS }) {
  if (!mode) return null;
  return (
    <button className="pill-btn install-btn" onClick={mode === "prompt" ? install : onIOS} title={t("install_app")}>
      <Icon name="download" size={15} /><span>{t("install_app")}</span>
    </button>
  );
}
