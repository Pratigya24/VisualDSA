import type { Config } from "tailwindcss";
import animate from "tailwindcss-animate";

/**
 * VisualDSA AI design tokens.
 *
 * Direction: dark-first developer tool (Linear / Raycast / GitHub / Vercel
 * territory), built around the product's actual subject matter — graphs,
 * trees, arrays, pointers — rather than a generic SaaS palette.
 *
 *  - Canvas is a cold near-black (#0A0B0F), never pure black, so glass
 *    surfaces have somewhere to catch light.
 *  - Signature accent is "trace" — an electric indigo used exclusively for
 *    the thing being tracked (the current pointer, the active call frame,
 *    the highlighted line). It never appears as decoration, only as
 *    "this is what's happening right now," which is the product's whole
 *    premise.
 *  - A second, cooler accent ("visited") marks state that has already been
 *    processed — visited nodes, completed steps — so a visualization can
 *    read at a glance without color explaining itself in prose.
 *  - Monospace (JetBrains Mono) is a first-class type role, not just a code
 *    font — variable names, complexity badges, and array indices all use it,
 *    reinforcing that this is a tool built by and for people who read code.
 */
export default {
  darkMode: ["class"],
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        canvas: {
          DEFAULT: "#0A0B0F",
          raised: "#111319",
          overlay: "#191C24",
          border: "#262A35",
        },
        ink: {
          DEFAULT: "#E7E9EE",
          muted: "#9AA1B2",
          faint: "#5C6376",
        },
        trace: {
          DEFAULT: "#6E5BFF",
          soft: "#6E5BFF1A",
          strong: "#8B7AFF",
        },
        visited: {
          DEFAULT: "#2FD3C6",
          soft: "#2FD3C61A",
        },
        signal: {
          success: "#3DD68C",
          warning: "#F5A623",
          danger: "#F0556B",
        },
      },
      fontFamily: {
        display: ["'Space Grotesk'", "system-ui", "sans-serif"],
        sans: ["'Inter'", "system-ui", "sans-serif"],
        mono: ["'JetBrains Mono'", "ui-monospace", "SFMono-Regular", "monospace"],
      },
      borderRadius: {
        sm: "6px",
        md: "10px",
        lg: "14px",
        xl: "20px",
      },
      boxShadow: {
        glass: "0 1px 0 0 rgba(255,255,255,0.04) inset, 0 8px 30px -12px rgba(0,0,0,0.6)",
        trace: "0 0 0 1px rgba(110,91,255,0.5), 0 0 24px -4px rgba(110,91,255,0.55)",
      },
      backdropBlur: {
        glass: "16px",
      },
      keyframes: {
        "pulse-trace": {
          "0%, 100%": { opacity: "1" },
          "50%": { opacity: "0.55" },
        },
      },
      animation: {
        "pulse-trace": "pulse-trace 1.6s ease-in-out infinite",
      },
    },
  },
  plugins: [animate],
} satisfies Config;
