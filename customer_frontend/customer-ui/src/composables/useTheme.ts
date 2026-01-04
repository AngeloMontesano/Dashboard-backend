import { ref } from 'vue';

type ThemeId = 'theme-classic' | 'theme-dark' | 'theme-ocean';

const STORAGE_KEY = 'customer_theme';
const current = ref<ThemeId>((sessionStorage.getItem(STORAGE_KEY) as ThemeId) || 'theme-classic');

export function useTheme() {
  function setTheme(id: ThemeId) {
    current.value = id;
    sessionStorage.setItem(STORAGE_KEY, id);
  }

  return { theme: current, setTheme };
}
