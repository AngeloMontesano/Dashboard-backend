import { createApp } from "vue";
import App from "./App.vue";
import "./styles/tokens.css";
import "./styles/base.css";
import "./styles/background/aurora.css";
import "./styles/layout.css";
import "./styles/components.css";
import "./styles/utilities.css";
import { initTheme } from "./theme/theme";

initTheme();

createApp(App).mount("#app");
