import { defineConfig, loadEnv } from 'vite';
import vue from '@vitejs/plugin-vue';
import path from 'path';

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '');
  const baseDomain = env.VITE_BASE_DOMAIN || 'test.myitnetwork.de';
  const tenantSlug = env.VITE_TENANT_SLUG;
  const allowedHosts = ['localhost', '127.0.0.1'];

  if (baseDomain && tenantSlug) {
    allowedHosts.push(`${tenantSlug}.${baseDomain}`);
  } else if (baseDomain) {
    allowedHosts.push(`*.${baseDomain}`);
  }

  return {
    plugins: [vue()],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, 'src')
      }
    },
    server: {
      port: 5173,
      host: '0.0.0.0',
      allowedHosts
    }
  };
});
