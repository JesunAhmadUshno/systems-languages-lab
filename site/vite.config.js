import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
// The site reads the level results JSON, READMEs and sources at build time, so every number on the page is generated, never typed.
export default defineConfig({
  base: '/systems-languages-lab/',
  plugins: [react()],
  server: { fs: { allow: ['..'] } },
});
