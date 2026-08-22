/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['"Inter"', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'Fira Code', 'Consolas', 'monospace'],
      },
      colors: {
        canvas: '#f8f6f3',
        // Rose Gold — primary accent
        rosegold: {
          50: '#faf5f3',
          100: '#f4e9e4',
          200: '#ead4cb',
          300: '#dfbcae',
          400: '#d0a291',
          500: '#bd8c7d',
          600: '#a8766a',
          700: '#8d6055',
          800: '#6f4c44',
          900: '#573d37',
        },
        // Soft Gold — secondary accent / success
        gold: {
          50: '#fbf9f4',
          100: '#f5efe2',
          200: '#ecdfc8',
          300: '#e0cca8',
          400: '#d6bb90',
          500: '#c9a97e',
          600: '#b39469',
          700: '#967b57',
          800: '#74603f',
        },
        // Silver — neutral lines & muted UI
        silver: {
          50: '#f7f7f8',
          100: '#eeeef0',
          200: '#dcdcde',
          300: '#c3c3c6',
          400: '#a9a9ad',
          500: '#8e8e90',
          600: '#757578',
          700: '#5f5f62',
        },
        // Onyx — text & dark surfaces
        onyx: {
          50: '#f5f5f5',
          100: '#e9e9ea',
          200: '#d3d3d5',
          300: '#adadb0',
          400: '#838386',
          500: '#6a6a6d',
          600: '#58585b',
          700: '#49494b',
          800: '#3b3b3d',
          900: '#303032',
          950: '#262628',
        },
      },
      boxShadow: {
        soft: '0 1px 3px rgba(87, 61, 55, 0.08), 0 1px 2px rgba(87, 61, 55, 0.05)',
        lift: '0 8px 24px -6px rgba(189, 140, 125, 0.25), 0 2px 6px rgba(87, 61, 55, 0.08)',
        glow: '0 0 32px -6px rgba(209, 191, 167, 0.45)',
      },
      keyframes: {
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-8px)' },
        },
      },
      animation: {
        shimmer: 'shimmer 2.2s linear infinite',
        float: 'float 5s ease-in-out infinite',
      },
    },
  },
  plugins: [],
}
