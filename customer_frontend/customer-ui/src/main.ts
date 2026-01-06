import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import { initTheme } from './composables/useTheme';
import { initTenantStatus } from './composables/useTenantStatus';
import './styles/tokens.css';
import './styles/base.css';
import './styles/utilities.css';
import './styles/layout.css';

async function bootstrap() {
  initTheme();
  await initTenantStatus();

  const app = createApp(App);
  app.use(router);
  await router.isReady();
  app.mount('#app');
}

void bootstrap();
