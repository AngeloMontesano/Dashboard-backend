import { onBeforeUnmount, ref } from "vue";
import { applyTheme, getTheme, onThemeChange, setTheme as persistTheme } from "../theme/theme";
import type { ResolvedTheme, ThemeMode } from "../theme/theme";

const theme = ref<ThemeMode>(getTheme());
const resolvedTheme = ref<ResolvedTheme>(applyTheme(theme.value));

export function useTheme() {
  const unsubscribe = onThemeChange((nextTheme, resolved) => {
    theme.value = nextTheme;
    resolvedTheme.value = resolved;
  });

  onBeforeUnmount(() => unsubscribe());

  function setTheme(mode: ThemeMode) {
    theme.value = mode;
    resolvedTheme.value = persistTheme(mode);
  }

  return { theme, resolvedTheme, setTheme };
}
