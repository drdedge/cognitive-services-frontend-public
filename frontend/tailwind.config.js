/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'background': '#F5F9FA',
        'header-bg': '#283857',
        'primary-action': '#4F78AB',
        'text-color': '#3B5781',
        'highlight': '#4F78AB',
        'success': '#28a745',
        'warning': '#ffc107',
        'azure': {
          50: '#e6f2ff',
          100: '#b3d9ff',
          200: '#80bfff',
          300: '#4da6ff',
          400: '#1a8cff',
          500: '#0078D4',  // Main Azure blue
          600: '#0066b8',
          700: '#00559c',
          800: '#004480',
          900: '#003366',
        },
        'primary': '#025B95',  // From existing code
        'error': '#D13438',
      },
      fontFamily: {
        sans: ['Segoe UI', 'system-ui', '-apple-system', 'sans-serif'],
      },
    },
  },
  plugins: [],
}