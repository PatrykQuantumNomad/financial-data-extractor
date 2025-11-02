import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: "jsdom",
    setupFiles: [path.resolve(__dirname, "./vitest.setup.ts")],
    transformMode: {
      web: [/\.tsx?$/, /\.jsx?$/],
      ssr: [/\.tsx?$/, /\.jsx?$/],
    },
    coverage: {
      provider: "v8",
      reporter: ["text", "json", "html"],
      exclude: [
        "node_modules/",
        "tests/",
        "**/*.test.{ts,tsx}",
        "**/*.spec.{ts,tsx}",
        "**/__tests__/**",
        "**/.next/**",
        "**/coverage/**",
        "**/*.config.{ts,js}",
        "**/*.d.ts",
        "next.config.js",
        "tailwind.config.ts",
        "postcss.config.mjs",
        "eslint.config.mjs",
      ],
    },
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "../src"),
      "@/lib": path.resolve(__dirname, "../src/lib"),
      "@/types": path.resolve(__dirname, "../src/types"),
      "@/components": path.resolve(__dirname, "../src/components"),
    },
  },
});
