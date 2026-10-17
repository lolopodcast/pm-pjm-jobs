/** Design tokens follow PRD 5.6 (interactive-learning-spa system): deep green #004030 + warm gold #D8C3A5. */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  darkMode: ["selector", '[data-theme="dark"]'],
  theme: {
    extend: {
      colors: {
        brand: { DEFAULT: "#004030", gold: "#D8C3A5" },
      },
      fontFamily: {
        sans: ["Inter", "Microsoft JhengHei", "PingFang TC", "Noto Sans TC", "system-ui", "sans-serif"],
        serif: ["Merriweather", "Microsoft JhengHei", "PingFang TC", "Noto Sans TC", "serif"],
      },
    },
  },
  plugins: [],
};
