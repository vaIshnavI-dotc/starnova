/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        canvas: {
          DEFAULT: '#090a0d',
          subtle: '#0d0f14',
          card: '#12141a',
          hover: '#181b22',
          border: '#20242f',
          borderLight: '#2c3242'
        },
        ink: {
          DEFAULT: '#eef0f4',
          muted: '#8e96a8',
          faint: '#545c6e'
        },
        accent: {
          DEFAULT: '#10b981', // muted emerald
          hover: '#059669',
          faint: 'rgba(16, 185, 129, 0.1)',
          border: 'rgba(16, 185, 129, 0.25)'
        },
        status: {
          backed: '#10b981',
          unchecked: '#f59e0b',
          no_evidence: '#ef4444'
        }
      },
      fontFamily: {
        mono: ['JetBrains Mono', 'ui-monospace', 'SFMono-Regular', 'Menlo', 'Monaco', 'Consolas', 'monospace'],
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0', transform: 'translateY(4px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideLeft: {
          '0%': { transform: 'translateX(100%)' },
          '100%': { transform: 'translateX(0)' },
        }
      },
      animation: {
        fade: 'fadeIn 0.2s ease-out forwards',
        slideIn: 'slideLeft 0.25s cubic-bezier(0.16, 1, 0.3, 1) forwards',
      }
    },
  },
  plugins: [],
}
