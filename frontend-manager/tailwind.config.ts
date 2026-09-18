import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./lib/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        canvas: "#0b0d14",
        sidebar: "#08090f",
        surface: "#141624",
        lift: "#1b1e2e",
        ink: {
          DEFAULT: "#f4f5fb",
          soft: "#c9cde0",
          muted: "#8b90a7",
          faint: "#5c6178",
        },
        line: {
          DEFAULT: "rgba(255,255,255,0.08)",
          strong: "rgba(255,255,255,0.14)",
        },
        brand: {
          DEFAULT: "#7c6cff",
          tint: "rgba(124,108,255,0.16)",
          accent: "#9d8cff",
        },
        good: { fg: "#4ade80", bg: "rgba(74,222,128,0.12)" },
        warn: { fg: "#fbbf24", bg: "rgba(251,191,36,0.12)" },
        stop: { fg: "#fb7185", bg: "rgba(251,113,133,0.12)" },
      },
      fontFamily: {
        sans: ["var(--font-inter)", "Inter", "ui-sans-serif", "system-ui", "sans-serif"],
      },
      boxShadow: {
        card: "0 12px 40px -24px rgb(0 0 0 / 0.6)",
      },
    },
  },
  plugins: [],
};

export default config;
