import { defineConfig } from 'vite';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  plugins: [tailwindcss()],
  build: {
    outDir: 'pup_sdk/web/static',  // Output to FastAPI static folder
    assetsDir: '',                 // Put assets directly in outDir
    rollupOptions: {
      input: 'frontend/style.css',  // Input CSS file
      output: {
        assetFileNames: 'style.css', // Name the output file
      }
    },
    emptyOutDir: false,            // Don't delete other static files
    minify: 'esbuild',             // Minify CSS
    sourcemap: false             // Don't include sourcemaps in production
  },
  server: {
    port: 3000,                   // Dev server port
    host: true                    // Allow external connections during dev
  }
});