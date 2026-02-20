import type { Config } from "tailwindcss";

export default {
  darkMode: ["class"],
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        nunito: ["var(--font-nunito)"],
        lexend: ["var(--font-lexend)"],
        inter: ["var(--font-inter)"],
        pingfang: ["PingFang SC", "system-ui", "sans-serif"],
      },
      colors: {
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        chart: {
          "1": "hsl(var(--chart-1))",
          "2": "hsl(var(--chart-2))",
          "3": "hsl(var(--chart-3))",
          "4": "hsl(var(--chart-4))",
          "5": "hsl(var(--chart-5))",
        },
      },
      borderRadius: {
        none: "0",
        xs: "clamp(2px, 0.1vw + 1.5px, 4px)",
        sm: "calc(var(--radius) - 4px)",
        md: "calc(var(--radius) - 2px)",
        lg: "var(--radius)",
        xl: "clamp(12px, 0.5vw + 8px, 16px)",
        "2xl": "clamp(16px, 0.6vw + 12px, 24px)",
        "3xl": "clamp(24px, 1vw + 16px, 32px)",
        "4xl": "clamp(32px, 1.2vw + 20px, 40px)",
        full: "9999px",
      },
      spacing: {
        none: "0",
        "3xs": "clamp(4px, 0.2vw + 2px, 6px)",
        "2xs": "clamp(8px, 0.3vw + 4px, 12px)",
        xs: "clamp(12px, 0.5vw + 8px, 16px)",
        sm: "clamp(16px, 0.8vw + 12px, 24px)",
        md: "clamp(24px, 1.2vw + 16px, 32px)",
        lg: "clamp(32px, 1.5vw + 24px, 48px)",
        xl: "clamp(48px, 2vw + 32px, 64px)",
        "2xl": "clamp(64px, 3vw + 48px, 96px)",
      },
      fontSize: {
        "display-lg": [
          "clamp(2.5rem, 4vw + 1.5rem, 4rem)",
          {
            lineHeight: "clamp(1.02, calc(1.02 + 0.05vw), 1.08)",
          },
        ],
        "display-base": [
          "clamp(2rem, 3vw + 1.25rem, 3rem)",
          {
            lineHeight: "clamp(1.05, calc(1.05 + 0.05vw), 1.1)",
          },
        ],
        "display-sm": [
          "clamp(1.75rem, 2.5vw + 1rem, 2.5rem)",
          {
            lineHeight: "clamp(1.08, calc(1.08 + 0.05vw), 1.15)",
          },
        ],
        "title-xl": [
          "clamp(1.75rem, 2vw + 1.25rem, 2.25rem)",
          {
            lineHeight: "clamp(1.08, calc(1.08 + 0.05vw), 1.15)",
          },
        ],
        "title-lg": [
          "clamp(1.5rem, 1.5vw + 1rem, 2rem)",
          {
            lineHeight: "clamp(1.1, calc(1.1 + 0.05vw), 1.2)",
          },
        ],
        "title-md": [
          "clamp(1.25rem, 1.2vw + 1rem, 1.75rem)",
          {
            lineHeight: "clamp(1.15, calc(1.15 + 0.05vw), 1.25)",
          },
        ],
        "title-sm": [
          "clamp(1.125rem, 1vw + 0.9rem, 1.5rem)",
          {
            lineHeight: "clamp(1.2, calc(1.2 + 0.05vw), 1.3)",
          },
        ],
        "title-xs": [
          "clamp(1rem, 0.8vw + 0.9rem, 1.25rem)",
          {
            lineHeight: "clamp(1.25, calc(1.25 + 0.05vw), 1.35)",
          },
        ],
        "body-lg": [
          "clamp(1.125rem, 0.5vw + 1rem, 1.25rem)",
          {
            lineHeight: "clamp(1.35, calc(1.35 + 0.05vw), 1.45)",
          },
        ],
        "body-base": [
          "clamp(1rem, 0.3vw + 0.9rem, 1.125rem)",
          {
            lineHeight: "clamp(1.4, calc(1.4 + 0.05vw), 1.5)",
          },
        ],
        "body-sm": [
          "clamp(0.875rem, 0.2vw + 0.8rem, 1rem)",
          {
            lineHeight: "clamp(1.45, calc(1.45 + 0.05vw), 1.55)",
          },
        ],
        "body-xs": [
          "clamp(0.75rem, 0.1vw + 0.7rem, 0.8125rem)",
          {
            lineHeight: "clamp(1.25, calc(1.25 + 0.05vw), 1.35)",
          },
        ],
        "caption-base": [
          "clamp(0.8125rem, 0.2vw + 0.75rem, 0.875rem)",
          {
            lineHeight: "clamp(1.25, calc(1.25 + 0.05vw), 1.35)",
          },
        ],
        "caption-sm": [
          "clamp(0.75rem, 0.1vw + 0.7rem, 0.8125rem)",
          {
            lineHeight: "clamp(1.25, calc(1.25 + 0.05vw), 1.35)",
          },
        ],
      },
      animation: {
        rippling: "rippling var(--duration) ease-out",
        "fade-in": "fadeIn 0.5s ease-in forwards",
      },
      keyframes: {
        rippling: {
          "0%": {
            opacity: "1",
          },
          "100%": {
            transform: "scale(2)",
            opacity: "0",
          },
        },
      },
    },
    plugins: ['require("tailwindcss-animate")'],
  },
} satisfies Config;
