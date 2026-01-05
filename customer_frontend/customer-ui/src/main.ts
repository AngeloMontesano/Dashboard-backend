import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import Aura from '@primevue/themes/aura';
import 'primeicons/primeicons.css';
import PrimeVue from 'primevue/config';
import ToastService from 'primevue/toastservice';
import './styles/tokens.css';
import './styles/layout.css';

const app = createApp(App);

app.use(ToastService);
app.use(router);
app.use(PrimeVue, {
  theme: {
    preset: Aura
  }
});
app.mount('#app');
