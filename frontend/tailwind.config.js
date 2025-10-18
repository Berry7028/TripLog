/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx}",
    "./components/**/*.{js,ts,jsx,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#568F87', // brand-teal
          dark: '#064232',    // brand-teal-dark
          foreground: '#ffffff'
        },
        accent: {
          DEFAULT: '#F5BABB', // accent-pink
          foreground: '#064232'
        },
        background: {
          DEFAULT: '#FFF5F2', // page-cream / light-gray
          panel: '#d9d9d9'
        },
        footer: '#064232'
      },
      borderRadius: {
        'card': '22px',
        'pill': '9999px'
      },
      fontFamily: {
        'mochiy': ['"Mochiy Pop P One"', 'system-ui', '-apple-system', 'sans-serif']
      }
    }
  },
  plugins: []
};
