import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Base path is configurable via env so the same build can be served either
// at the root (npm run dev / npm run start) or under a sub-path like /quiz/
// (static deploy alongside the SNB marketing site on Netlify).
export default defineConfig({
  base: process.env.VITE_BASE || "/",
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      "/api": {
        target: "http://localhost:3001",
        changeOrigin: true,
      },
    },
  },
});
