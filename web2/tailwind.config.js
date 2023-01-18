/** @type {import('tailwindcss').Config} */
module.exports = {
  mode: 'jit',
  content: [
      './adminstration/templates/**/*.html',
      './parkings/templates/**/*.html',
      './users/templates/**/*.html',
      './templates/**/*.html',
      './node_modules/flowbite/**/*.js'
  ],
  theme: {
    screens: {
      'sm': '640px',
      'md': '768px',
      'lg': '1024px',
      'xl': '1280px',
      '2xl': '1536px',
     },
    extend: {
      minWidth: {
        '24': '6rem',
      },
    },
  },
  plugins: [
    require('flowbite/plugin')
  ],
}
