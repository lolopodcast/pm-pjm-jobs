import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { VitePWA } from "vite-plugin-pwa";
import pkg from "./package.json" with { type: "json" };

// PRD 8.2: only our own origin, no inline scripts, no eval. Added at build time only, because the
// dev server injects an inline script for hot reload.
const CSP = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; " +
  "font-src 'self'; connect-src 'self'; manifest-src 'self'; worker-src 'self'; base-uri 'self'; form-action 'none'";
const cspPlugin = {
  name: "csp",
  apply: "build",
  transformIndexHtml: (html) =>
    html.replace("<meta charset=\"UTF-8\" />", `<meta charset="UTF-8" />\n    <meta http-equiv="Content-Security-Policy" content="${CSP}" />`),
};

// Served from https://lolopodcast.github.io/pm-pjm-jobs/
export default defineConfig({
  base: "/pm-pjm-jobs/",
  // Only the code version goes into the bundle. A build date here would change the bundle on every
  // daily deploy and make returning visitors see an "update available" prompt each day.
  define: { __APP_VERSION__: JSON.stringify(pkg.version) },
  plugins: [
    react(),
    cspPlugin,
    VitePWA({
      registerType: "prompt",
      includeAssets: ["icon.svg"],
      manifest: {
        name: "上市櫃 PM／PjM 新人職缺觀測站",
        short_name: "PM 職缺觀測",
        description: "104 人力銀行上市櫃 PM／PjM 新人職缺與 AI 職能分析（教學用途）",
        lang: "zh-Hant-TW",
        theme_color: "#004030",
        background_color: "#f4f4f4",
        display: "standalone",
        icons: [{ src: "icon.svg", sizes: "any", type: "image/svg+xml", purpose: "any maskable" }],
      },
      workbox: {
        // App files are precached (hashed names). Data JSON is network-first so users get today's
        // data when online and the last copy when offline (PRD 11.4).
        globPatterns: ["**/*.{js,css,html,svg,woff2}"],
        runtimeCaching: [{
          urlPattern: ({ url }) => url.pathname.includes("/data/") && url.pathname.endsWith(".json"),
          handler: "NetworkFirst",
          options: { cacheName: "data", networkTimeoutSeconds: 8, expiration: { maxEntries: 20 } },
        }],
      },
    }),
  ],
  test: { environment: "node" },
});
