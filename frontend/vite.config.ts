import { fileURLToPath, URL } from "node:url";
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
    },
  },
  server: {
    // proxy /v1/* to the dockerized api so the dev server stays same-origin
    // with the bundle's relative VITE_API_BASE_URL=/v1. that way no CORS in
    // dev OR prod -- the api always lives at the same origin as the SPA.
    proxy: {
      "/v1": {
        target: "http://localhost:8080",
        changeOrigin: true,
      },
    },
  },
});
