export type ThemeMode = "light" | "dark" | "system";
export type ResolvedTheme = "light" | "dark";

const STORAGE_KEY = "admin_theme";
let currentTheme: ThemeMode = "system";
let currentResolved: ResolvedTheme = "light";
let mediaListenerAttached = false;
const listeners = new Set<(theme: ThemeMode, resolved: ResolvedTheme) => void>();

function readStoredTheme(): ThemeMode {
  if (typeof window === "undefined") return currentTheme;
  const stored = localStorage.getItem(STORAGE_KEY) as ThemeMode | null;
  return stored || "system";
}

function resolveTheme(mode: ThemeMode): ResolvedTheme {
  if (mode === "system") {
    if (typeof window !== "undefined" && window.matchMedia) {
      return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
    }
    return "light";
  }
  return mode;
}

function notify() {
  listeners.forEach((listener) => listener(currentTheme, currentResolved));
}

export function getTheme(): ThemeMode {
  currentTheme = readStoredTheme();
  return currentTheme;
}

export function applyTheme(mode: ThemeMode): ResolvedTheme {
  currentResolved = resolveTheme(mode);
  if (typeof document !== "undefined") {
    const root = document.documentElement;
    root.dataset.theme = currentResolved;
    root.classList.toggle("theme-dark", currentResolved === "dark");
    root.classList.toggle("theme-classic", currentResolved !== "dark");
  }
  notify();
  return currentResolved;
}

export function setTheme(mode: ThemeMode): ResolvedTheme {
  currentTheme = mode;
  if (typeof window !== "undefined") {
    localStorage.setItem(STORAGE_KEY, mode);
  }
  return applyTheme(mode);
}

export function initTheme(): void {
  const stored = getTheme();
  applyTheme(stored);

  if (typeof window !== "undefined" && window.matchMedia && !mediaListenerAttached) {
    const media = window.matchMedia("(prefers-color-scheme: dark)");
    const handler = () => {
      if (currentTheme === "system") {
        applyTheme("system");
      }
    };
    media.addEventListener("change", handler);
    mediaListenerAttached = true;
  }
}

export function onThemeChange(listener: (theme: ThemeMode, resolved: ResolvedTheme) => void) {
  listeners.add(listener);
  return () => listeners.delete(listener);
}
