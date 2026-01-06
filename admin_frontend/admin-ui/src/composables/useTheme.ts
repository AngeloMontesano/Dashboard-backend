import { ref } from "vue";

type ThemeMode = "light" | "dark" | "system";

const STORAGE_KEY = "admin_theme";
const theme = ref<ThemeMode>("system");
const resolvedTheme = ref<"light" | "dark">("light");
let mediaListenerAttached = false;

function apply(mode: ThemeMode) {
  const effective =
    mode === "system"
      ? window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches
        ? "dark"
        : "light"
      : mode;

  resolvedTheme.value = effective;
  document.documentElement.dataset.theme = effective;
  document.documentElement.classList.toggle("theme-dark", effective === "dark");
  document.documentElement.classList.toggle("theme-classic", effective !== "dark");
}

export function initTheme() {
  const stored = localStorage.getItem(STORAGE_KEY) as ThemeMode | null;
  theme.value = stored || "system";
  apply(theme.value);

  if (typeof window !== "undefined" && window.matchMedia && !mediaListenerAttached) {
    const media = window.matchMedia("(prefers-color-scheme: dark)");
    const handler = () => {
      if (theme.value === "system") apply("system");
    };
    media.addEventListener("change", handler);
    mediaListenerAttached = true;
  }
}

export function useTheme() {
  function setTheme(mode: ThemeMode) {
    theme.value = mode;
    localStorage.setItem(STORAGE_KEY, mode);
    apply(mode);
  }

  return { theme, resolvedTheme, setTheme };
}
