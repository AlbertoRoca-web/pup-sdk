/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './pup_sdk/web/templates/**/*.html',  // Scan HTML templates
    './pup_sdk/web/**/*.py',              // Scan Python files for inline styles
    './frontend/**/*.css'                 // Scan frontend CSS files
  ],
  theme: {
    extend: {
      // Add any custom theme extensions here if needed
    },
  },
  plugins: [
    // Add any Tailwind plugins here if needed
  ],
}