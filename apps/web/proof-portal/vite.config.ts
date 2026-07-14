/// <reference types="vitest/config" />

import path from "path";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@project-ai/web-shared": path.resolve(__dirname, "../shared/src/index.ts"),
    },
  },
  server: {
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8000",
        rewrite: (p) => p.replace(/^\/api/, ""),
      },
    },
  },
  test: { environment: "jsdom", setupFiles: "./src/test-setup.ts" },
});
