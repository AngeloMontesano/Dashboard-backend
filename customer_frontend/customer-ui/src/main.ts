import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import PrimeVue from 'primevue/config';
import ToastService from 'primevue/toastservice';
import Lara from '@primevue/themes/lara';
import 'primeicons/primeicons.css';
import './styles/tokens.css';
import './styles/layout.css';
import PrimeVue from 'primevue/config';
import Aura from '@primevue/themes/aura';
import 'primeicons/primeicons.css';

const app = createApp(App);

app.use(PrimeVue, { ripple: true, theme: { preset: Lara } });
app.use(ToastService);
app.use(router);
app.use(PrimeVue, {
  theme: {
    preset: Aura
  }
});
app.mount('#app');
