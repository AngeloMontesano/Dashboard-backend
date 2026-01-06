<!-- src/App.vue -->
<template>
  <!--
    App Root
    Ziele
    - Zentrale Layout Shell (Sidebar + Main)
    - Zentrale Theme Steuerung (dark class)
    - Zentrale System Checks (API/DB)
    - Zentrales Toast Rendering (alle Views nutzen nur toast())
    - Sections links sind gekoppelt an Content rechts (keine "toten" Menüs)
  -->
  <div :class="['app', appThemeClass]">
    <template v-if="!ui.authenticated">
      <AdminLoginView @loggedIn="applyLogin" />
    </template>
    <template v-else>
      <div class="shell">
        <!-- =========================================================
             SIDEBAR
        ========================================================== -->
        <aside class="sidebar">
          <!-- Brand -->
          <div class="brand">
            <div class="logo">LV</div>
            <div class="brandText">
              <div class="brandTitle">Lagerverwaltung</div>
              <div class="brandSub">Admin Portal</div>
            </div>
          </div>

          <!-- Navigation -->
          <nav class="nav">
            <button
              v-for="item in sections"
              :key="item.id"
              class="navItem"
              :class="{ active: ui.section === item.id }"
              @click="goSection(item.id)"
            >
              <span class="navIcon">{{ item.icon }}</span>
              <span class="navLabel">{{ item.label }}</span>
            </button>
          </nav>

          <div class="sidebar-divider"></div>
          <div class="navGroup">
            <div class="navGroupTitle">Globale Einstellungen</div>
            <ul class="navGroupList">
              <li>Globale Artikel</li>
              <li>Globale Kategorien</li>
              <li>Globale Typen</li>
              <li>Globale Branchen</li>
            </ul>
          </div>

          <!-- Bottom Area -->
          <div class="sideBottom">
            <!-- System Status -->
            <div class="sysBlock">
              <div class="sysTitle">System</div>

              <div class="sysRow">
                <div class="statusInline">
                  <span class="statusDot" :class="api.ok ? 'ok' : 'bad'"></span>
                  <span class="statusLabel">API erreichbar</span>
                </div>
              </div>

            <div class="sysRow">
              <div class="statusInline">
                <span class="statusDot" :class="db.ok ? 'ok' : 'bad'"></span>
                <span class="statusLabel">DB erreichbar</span>
              </div>
              </div>
            </div>

            <div class="divider"></div>

            <!-- Theme Quick Toggle -->
            <div class="toggle">
              <span>Theme</span>
              <select class="input full-width" :value="theme.value" @change="onThemeSelect">
                <option value="system">System</option>
                <option value="light">Light</option>
                <option value="dark">Dark</option>
              </select>
            </div>
          </div>
        </aside>

        <!-- =========================================================
             MAIN
        ========================================================== -->
        <main class="main">
          <!-- Topbar -->
          <header :class="['topbar', ui.section === 'kunden' ? 'topbar-flat' : '']">
            <div class="topLeft">
              <div class="titleRow">
                <div class="pageTitle">{{ pageTitle }}</div>
                <div class="crumbs">{{ breadcrumb }}</div>
              </div>
              <div class="pageHint">{{ pageSubtitle }}</div>
            </div>

            <div class="topRight">
              <div class="topActions">
                <button class="btnGhost small" @click="quickRefresh" :disabled="busy.refresh">
                  {{ busy.refresh ? "..." : "Refresh" }}
                </button>
                <button class="btnGhost small" @click="logout">Abmelden</button>
              </div>
            </div>
          </header>

          <!-- Workspace -->
          <section class="workspace">
            <!-- SECTION: Kunden -->
            <AdminTenantsView
              v-if="ui.section === 'kunden'"
              :adminKey="ui.adminKey"
              :actor="ui.actor"
              :apiOk="api.ok"
              :dbOk="db.ok"
              :selectedTenantId="tenantContext.id"
              @openMemberships="openMemberships"
              @tenantSelected="setTenantContext"
            />

          <!-- SECTION: Users -->
            <AdminUsersView
              v-else-if="ui.section === 'users'"
              :adminKey="ui.adminKey"
              :actor="ui.actor"
              :apiOk="api.ok"
              :dbOk="db.ok"
            />

          <!-- SECTION: Tenant Users / Memberships -->
            <AdminMembershipsView
              v-else-if="ui.section === 'memberships'"
              :adminKey="ui.adminKey"
              :actor="ui.actor"
              :apiOk="api.ok"
              :dbOk="db.ok"
              :selectedTenantId="tenantContext.id"
              @tenantSelected="setTenantContext"
            />

          <!-- SECTION: Operations -->
            <AdminOperationsView
              v-else-if="ui.section === 'operations'"
              :adminKey="ui.adminKey"
              :actor="ui.actor"
              :apiOk="api.ok"
              :dbOk="db.ok"
              :initialTab="operationsTab"
              :tenant="tenantContext"
              @tabChange="setOperationsTab"
            />

          <!-- SECTION: Settings -->
            <AdminSettingsView
              v-else
              :adminKey="ui.adminKey"
              :actor="ui.actor"
              :apiOk="api.ok"
              :dbOk="db.ok"
              :theme="theme.value"
              :apiBase="apiBase"
              :baseDomain="baseDomain"
              @setTheme="setTheme"
              @resetContext="resetContext"
            />
          </section>
        </main>
      </div>
    </template>

    <!-- =========================================================
         ZENTRALER TOAST
         - Alle Views nutzen useToast().toast(...)
         - Nur App.vue rendert ToastHost
    ========================================================== -->
    <ToastHost />
  </div>
</template>

<script setup lang="ts">
/*
  App.vue
  Architektur Entscheidungen
  - Layout/Design über globale CSS Dateien (tokens.css, base.css, layout.css)
  - App.vue enthält KEIN <style scoped>
  - Toast ist zentral (kein Toast Markup in Views, ToastHost am Root)
  - Checks laufen über platform endpoints:
      GET /health
      GET /health/db
    BaseURL läuft immer über den Proxy-Pfad /api
*/

import { computed, onBeforeUnmount, onMounted, reactive, ref } from "vue";
import { useToast } from "./composables/useToast";
import { platformHealth, platformHealthDb } from "./api/platform";
import { getBaseDomain, getBaseURL } from "./api/base";
import { useTheme } from "./composables/useTheme";

/* Views */
import AdminTenantsView from "./views/AdminTenantsView.vue";
import AdminUsersView from "./views/AdminUsersView.vue";
import AdminMembershipsView from "./views/AdminMembershipsView.vue";
import AdminSettingsView from "./views/AdminSettingsView.vue";
import AdminLoginView from "./views/AdminLoginView.vue";
import ToastHost from "./components/common/ToastHost.vue";
import AdminOperationsView from "./views/AdminOperationsView.vue";

/* Zentraler Toast State */
const { toast } = useToast();
const baseDomain = getBaseDomain();
const apiBase = getBaseURL();
const ADMIN_AUTH_STORAGE_KEY = "admin_auth";

type OperationsTab = "overview" | "health" | "audit" | "snapshot";

/* Sidebar Sections */
const sections = [
  { id: "kunden", label: "Kunden", icon: "👥" },
  { id: "memberships", label: "Tenant-User", icon: "🧩" },
  { id: "operations", label: "Operations", icon: "🛠️" },
  { id: "users", label: "Benutzer", icon: "👤" },
  { id: "settings", label: "Einstellungen", icon: "⚙️" },
] as const;

type SectionId = (typeof sections)[number]["id"];

/* UI State */
// TODO: Entfernen, sobald Admin-APIs ohne expliziten adminKey/actor auskommen.
const ui = reactive({
  actor: "",
  adminKey: "",
  authenticated: false,
  section: "kunden" as SectionId,
});

const operationsTab = ref<OperationsTab>("overview");
const { theme, resolvedTheme, setTheme } = useTheme();
const appThemeClass = computed(() => (resolvedTheme.value === "dark" ? "theme-dark" : "theme-classic"));

const tenantContext = reactive({
  id: localStorage.getItem("adminSelectedTenantId") || "",
  name: localStorage.getItem("adminSelectedTenantName") || "",
  slug: localStorage.getItem("adminSelectedTenantSlug") || "",
});

/* Busy Flags */
const busy = reactive({
  refresh: false,
});

/* System Status */
const api = reactive({ ok: false, busy: false });
const db = reactive({ ok: false, busy: false });

/* Navigation */
function goSection(sectionId: SectionId) {
  ui.section = sectionId;
  if (sectionId === "operations") {
    pushOperationsRoute(operationsTab.value);
  } else {
    const targetPath = sectionId === "kunden" ? "/" : `/${sectionId}`;
    window.history.pushState({}, "", targetPath);
  }
}

function setTenantContext(payload: { id: string; name: string; slug: string } | null) {
  tenantContext.id = payload?.id || "";
  tenantContext.name = payload?.name || "";
  tenantContext.slug = payload?.slug || "";
  if (payload?.id) {
    localStorage.setItem("adminSelectedTenantId", payload.id);
    localStorage.setItem("adminSelectedTenantName", payload.name || "");
    localStorage.setItem("adminSelectedTenantSlug", payload.slug || "");
  } else {
    localStorage.removeItem("adminSelectedTenantId");
    localStorage.removeItem("adminSelectedTenantName");
    localStorage.removeItem("adminSelectedTenantSlug");
  }
}

function clearTenantContext() {
  setTenantContext(null);
}

function applyLogin(payload: { adminKey: string; actor: string }) {
  ui.adminKey = payload.adminKey;
  ui.actor = payload.actor || "admin";
  ui.authenticated = true;
  sessionStorage.setItem(
    ADMIN_AUTH_STORAGE_KEY,
    JSON.stringify({ adminKey: ui.adminKey, actor: ui.actor })
  );
  quickRefresh();
}

/* Titles */
const pageTitle = computed(() => {
  const m: Record<SectionId, string> = {
    kunden: "Kunden",
    users: "Benutzer",
    memberships: "Tenant-User",
    operations: "Operations",
    settings: "Einstellungen",
  };
  return m[ui.section];
});

const pageSubtitle = computed(() => {
  if (ui.section === "kunden") return "Tenants suchen, auswählen, Details & Aktionen";
  if (ui.section === "users") return "Admin-Portal Benutzer verwalten";
  if (ui.section === "memberships") return "User mit Tenants verknüpfen und Rollen setzen";
  if (ui.section === "operations") return "Health, Audit, Snapshots und Logs";
  return "Security, Theme, Feature Flags";
});

const breadcrumb = computed(() => {
  if (tenantContext.slug) {
    return `${pageTitle.value} / ${tenantContext.slug}`;
  }
  return pageTitle.value;
});

/* Checks */
async function checkApi() {
  api.busy = true;
  try {
    await platformHealth();
    api.ok = true;
  } catch {
    api.ok = false;
    toast("API nicht erreichbar", "danger");
  } finally {
    api.busy = false;
  }
}

async function checkDb() {
  db.busy = true;
  try {
    await platformHealthDb();
    db.ok = true;
  } catch {
    db.ok = false;
    toast("DB nicht erreichbar", "danger");
  } finally {
    db.busy = false;
  }
}

/* Quick Refresh: beide Checks nacheinander */
async function quickRefresh() {
  busy.refresh = true;
  try {
    await checkApi();
    await checkDb();
  } finally {
    busy.refresh = false;
  }
}

function resetContext() {
  ui.adminKey = "";
  ui.actor = "";
  ui.authenticated = false;
  sessionStorage.removeItem(ADMIN_AUTH_STORAGE_KEY);
}

/* Boot */
onMounted(async () => {
  syncFromLocation();
  const storedAuth = sessionStorage.getItem(ADMIN_AUTH_STORAGE_KEY);
  if (storedAuth) {
    try {
      const parsed = JSON.parse(storedAuth) as { adminKey?: string; actor?: string };
      ui.adminKey = parsed.adminKey || "";
      ui.actor = parsed.actor || "";
      ui.authenticated = Boolean(ui.adminKey);
    } catch {
      sessionStorage.removeItem(ADMIN_AUTH_STORAGE_KEY);
    }
  }
  window.addEventListener("popstate", syncFromLocation);
  await quickRefresh();
});

function onThemeSelect(event: Event) {
  const mode = (event.target as HTMLSelectElement).value as "light" | "dark" | "system";
  setTheme(mode);
}

function openMemberships(tenantId: string) {
  goSection("memberships");
  if (tenantId) localStorage.setItem("adminSelectedTenantId", tenantId);
}

function logout() {
  ui.adminKey = "";
  ui.actor = "";
  ui.authenticated = false;
  ui.section = "kunden";
  window.history.pushState({}, "", "/login");
}

function pushOperationsRoute(tab: OperationsTab) {
  const query = tab ? `?tab=${tab}` : "";
  window.history.pushState({}, "", `/operations${query}`);
}

function setOperationsTab(tab: OperationsTab) {
  operationsTab.value = tab;
  if (ui.section === "operations") {
    const currentPath = window.location.pathname;
    const currentTab = new URLSearchParams(window.location.search).get("tab");
    const desiredPath = `/operations${tab ? `?tab=${tab}` : ""}`;
    if (currentPath !== "/operations" || currentTab !== tab) {
      window.history.pushState({}, "", desiredPath);
    }
  }
}

function syncFromLocation() {
  const path = window.location.pathname;
  const params = new URLSearchParams(window.location.search);
  const tabFromQuery = params.get("tab") as OperationsTab | null;

  if (path === "/operations") {
    ui.section = "operations";
    if (tabFromQuery && ["overview", "health", "audit", "snapshot"].includes(tabFromQuery)) {
      operationsTab.value = tabFromQuery;
    } else {
      operationsTab.value = "overview";
    }
    return;
  }

  if (path === "/diagnostics") {
    ui.section = "operations";
    operationsTab.value = "health";
    window.history.replaceState({}, "", "/operations?tab=health");
    return;
  }

  if (path === "/audit") {
    ui.section = "operations";
    operationsTab.value = "audit";
    window.history.replaceState({}, "", "/operations?tab=audit");
    return;
  }

  const sectionPathMap: Record<string, SectionId> = {
    "/": "kunden",
    "/kunden": "kunden",
    "/users": "users",
    "/memberships": "memberships",
    "/settings": "settings",
  };

  if (sectionPathMap[path]) {
    ui.section = sectionPathMap[path];
  }
}

onBeforeUnmount(() => {
  window.removeEventListener("popstate", syncFromLocation);
});
</script>

<style>
.topbar-flat {
  background: transparent;
  border: none;
  box-shadow: none;
  padding: 0;
  margin: 0 0 4px 0;
}

.topbar-flat .topRight {
  align-items: center;
}

.topActions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.pageHint {
  color: var(--muted);
  margin-top: 4px;
}

/* Sidebar kompakter */
.shell {
  align-items: start;
}

.sidebar {
  height: fit-content;
  position: sticky;
  top: 12px;
  align-self: start;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.nav {
  align-self: start;
  height: fit-content;
}

.sideBottom {
  align-self: start;
  margin-top: 4px;
}

.topbar.topbar-flat {
  padding: 10px 12px 12px;
  min-height: unset;
}
</style>
