import { defineConfig, loadEnv } from "vite";
import vue from "@vitejs/plugin-vue";
import { resolve } from "path";

/// <reference types="vitest" />

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd());

  return {
    plugins: [vue()],
    resolve: {
      alias: {
        "@": resolve(__dirname, "src"),
        "@components": resolve(__dirname, "src/components"),
        "@views": resolve(__dirname, "src/views"),
        "@api": resolve(__dirname, "src/api"),
        "@stores": resolve(__dirname, "src/stores"),
        "@utils": resolve(__dirname, "src/utils"),
        "@layouts": resolve(__dirname, "src/layouts"),
      },
    },
    test: {
      globals: true,
      environment: "node",
    },
    server: {
      port: parseInt(env.VITE_APP_PORT || "3000"),
      host: true,
      open: true,
      proxy: {
        "/api": {
          target: "http://localhost:8000",
          changeOrigin: true
        }
      }
    },
    build: {
      outDir: "dist",
      assetsDir: "assets",
      assetsInlineLimit: 4096,
      minify: "terser",
      terserOptions: {
        compress: {
          drop_console: mode === "production",
          drop_debugger: mode === "production",
        },
      },
      rollupOptions: {
        output: {
          manualChunks: {
            vendor: ["vue", "vue-router", "pinia"],
            element: ["element-plus", "@element-plus/icons-vue"],
            echarts: ["echarts"],
          },
        },
      },
    },
    css: {
      preprocessorOptions: {
        scss: {
          additionalData: `@import "@/styles/variables.scss";`,
        },
      },
    },
  };
});
