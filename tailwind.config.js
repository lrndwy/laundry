const { addDynamicIconSelectors } = require("@iconify/tailwind")

/** @type {import('tailwindcss').Config} */
export default {
    content: [
        './templates/**/*.html',
        './templates/*.html',
        './node_modules/flyonui/dist/js/*.js',
        './node_modules/flatpickr/dist/flatpickr.js',
        './static/js/*.js',
    ],
    theme: {
        extend: {},
    },
    plugins: [
        // Iconify plugin
        addDynamicIconSelectors(),
        require('flyonui'),
        require('flyonui/plugin'),
        require('tailwindcss-motion')
    ],
    flyonui: {
      vendors: true // Enable vendor-specific CSS generation
    }
}
