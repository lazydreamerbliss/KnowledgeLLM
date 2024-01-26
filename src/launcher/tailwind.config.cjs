// we do not use tailwind lib in this project, we load it from CDN when loading the page
// but we need this file to get tailwind css intellisense extension working

/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{html,js,jsx,ts,tsx}"],
  theme: {
    extend: {},
  },
  plugins: [],
}
