import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./lib/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ice: "#EAF2FB",
        canvas: "#F4F7FC",
        surface: "#FFFFFF",
        mist: "#C5CAD3",
        ink: {
          DEFAULT: "#111111",
          soft: "#3D3D3D",
          muted: "#6B6B6B",
          faint: "#9AA0A8",
        },
        line: {
          DEFAULT: "#E4E9F0",
          strong: "#C5CAD3",
        },
        brand: {
          DEFAULT: "#0033CC",
          deep: "#001A80",
          hover: "#002BB3",
          ice: "#E8F0FF",
          line: "#B8C9FF",
        },
        good: { fg: "#15803D", bg: "#E9F8EE", line: "#BBEBCB" },
        warn: { fg: "#B45309", bg: "#FEF6E7", line: "#F6DFAE" },
        stop: { fg: "#B42318", bg: "#FEF0EF", line: "#F9D3D0" },
      },
      fontFamily: {
        sans: ["var(--font-jakarta)", "Plus Jakarta Sans", "ui-sans-serif", "system-ui", "sans-serif"],
      },
      fontSize: {
        "2xs": ["11px", { lineHeight: "16px" }],
        xs: ["12px", { lineHeight: "18px" }],
        sm: ["13px", { lineHeight: "20px" }],
        base: ["14px", { lineHeight: "22px" }],
        md: ["15px", { lineHeight: "24px" }],
        lg: ["17px", { lineHeight: "26px" }],
        xl: ["20px", { lineHeight: "28px" }],
        "2xl": ["26px", { lineHeight: "34px" }],
        "3xl": ["32px", { lineHeight: "40px" }],
      },
      borderRadius: {
        bubble: "22px",
        card: "24px",
        field: "16px",
        sheet: "32px",
      },
      boxShadow: {
        card: "0 8px 24px -12px rgb(0 26 128 / 0.18), 0 1px 2px 0 rgb(17 17 17 / 0.04)",
        lift: "0 16px 40px -20px rgb(0 26 128 / 0.28)",
        composer: "0 -8px 24px -16px rgb(0 26 128 / 0.12)",
      },
      maxWidth: {
        thread: "720px",
        phone: "430px",
      },
      keyframes: {
        "dot-bounce": {
          "0%, 60%, 100%": { transform: "translateY(0)", opacity: "0.4" },
          "30%": { transform: "translateY(-3px)", opacity: "1" },
        },
        "bubble-in": {
          from: { opacity: "0", transform: "translateY(8px)" },
          to: { opacity: "1", transform: "translateY(0)" },
        },
      },
      animation: {
        "dot-bounce": "dot-bounce 1.1s ease-in-out infinite",
        "bubble-in": "bubble-in 240ms cubic-bezier(0.22, 1, 0.36, 1)",
      },
      transitionTimingFunction: {
        swift: "cubic-bezier(0.22, 1, 0.36, 1)",
      },
    },
  },
  plugins: [],
};

export default config;
