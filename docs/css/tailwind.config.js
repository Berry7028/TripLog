/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "../*.html",
    "../js/*.js"
  ],
  theme: {
    extend: {
      fontFamily: {
        'mochiy': ['Mochiy Pop P One', 'cursive'],
      },
      colors: {
        'brand-teal': '#568F87',
        'brand-teal-dark': '#064232',
        'accent-pink': '#F5BABB',
        'page-cream': '#FFF5F2',
      },
      backgroundImage: {
        'brand-gradient': 'linear-gradient(135deg, #568F87, #064232)',
        'accent-gradient': 'linear-gradient(135deg, #F5BABB, #e8a4a5)',
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        }
      }
    },
  },
  plugins: [],
}
