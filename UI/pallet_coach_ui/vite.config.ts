import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    // Proxy configuration: forwards requests starting with /api and /output
    // to the backend API running on http://127.0.0.1:8000
    // This helps avoid CORS issues during development
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,  // Change the origin header in the request
      },
      "/output": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,  // Change the origin header in the request
      },
    },
  },
  test: {
    environment: "jsdom",
    setupFiles: "./src/test/setup.ts",
  },
});
