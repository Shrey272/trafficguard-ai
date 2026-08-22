/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        dark: {
          bg: '#0b0d14',
          sidebar: '#121621',
          panel: '#1a1e2b',
          border: '#2a2f42',
          text: '#94a3b8'
        }
      }
    },
  },
  plugins: [],
}
