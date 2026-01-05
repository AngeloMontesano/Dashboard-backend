import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import path from "path";

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      axios: path.resolve(__dirname, "node_modules/axios/index.js"),
    },
  },
  server: {
    port: 5173,
    strictPort: true,
    host: true,
    allowedHosts: ["admin.test.myitnetwork.de"],
  },
});
