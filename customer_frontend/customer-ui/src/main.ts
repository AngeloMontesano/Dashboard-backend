import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import { initTheme } from './composables/useTheme';
import './styles/tokens.css';
import './styles/base.css';
import './styles/utilities.css';
import './styles/layout.css';

initTheme();

const app = createApp(App);

app.use(router);
app.mount('#app');
