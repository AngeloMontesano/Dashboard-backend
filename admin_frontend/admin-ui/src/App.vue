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
  <div :class="['app', ui.dark ? 'dark' : '']">
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

        <!-- Bottom Area -->
        <div class="sideBottom">
          <!-- System Status -->
          <div class="sysBlock">
            <div class="sysTitle">System</div>

            <div class="sysRow">
              <div class="statusPill" :class="api.ok ? 'ok' : 'bad'">
                <span class="dot"></span>
                <span>API {{ api.ok ? "erreichbar" : "nicht erreichbar" }}</span>
              </div>
              <button class="btnPrimary small" :disabled="api.busy" @click="checkApi">
                {{ api.busy ? "prüfe..." : "Prüfen" }}
              </button>
            </div>

            <div class="sysRow">
              <div class="statusPill" :class="db.ok ? 'ok' : 'bad'">
                <span class="dot"></span>
                <span>DB {{ db.ok ? "erreichbar" : "nicht erreichbar" }}</span>
              </div>
              <button class="btnGhost small" :disabled="db.busy" @click="checkDb">
                {{ db.busy ? "prüfe..." : "Prüfen" }}
              </button>
            </div>
          </div>

          <div class="divider"></div>

          <!-- Darkmode -->
          <label class="toggle">
            <input type="checkbox" v-model="ui.dark" />
            <span>Darkmode</span>
          </label>

          <!-- Admin Context -->
          <div class="sideFields">
            <div class="field">
              <div class="label">Actor</div>
              <input class="input" v-model.trim="ui.actor" placeholder="admin" />
            </div>

            <div class="field">
              <div class="label">Admin Key</div>
              <input class="input" v-model.trim="ui.adminKey" placeholder="X-Admin-Key" type="password" />
            </div>
          </div>

          <div class="hintBox">
            Admin Endpunkte benötigen <span class="mono">X-Admin-Key</span>. Key wird nur im Memory gehalten.
          </div>
        </div>
      </aside>

      <!-- =========================================================
           MAIN
      ========================================================== -->
      <main class="main">
        <!-- Topbar -->
        <header class="topbar">
          <div class="topLeft">
            <div class="titleRow">
              <div class="pageTitle">{{ pageTitle }}</div>
              <div class="crumbs">{{ pageSubtitle }}</div>
            </div>
          </div>

          <div class="topRight">
            <button class="btnGhost" @click="quickRefresh" :disabled="busy.refresh">
              {{ busy.refresh ? "..." : "Refresh" }}
            </button>
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
          />

          <!-- SECTION: Audit -->
          <AdminAuditView
            v-else-if="ui.section === 'audit'"
            :adminKey="ui.adminKey"
            :actor="ui.actor"
          />

          <!-- SECTION: Diagnostics -->
          <AdminDiagnosticsView
            v-else-if="ui.section === 'diagnostics'"
            :adminKey="ui.adminKey"
            :actor="ui.actor"
            :apiOk="api.ok"
            :dbOk="db.ok"
          />

          <!-- SECTION: Settings -->
          <AdminSettingsView
            v-else
            :adminKey="ui.adminKey"
            :actor="ui.actor"
            :apiOk="api.ok"
            :dbOk="db.ok"
            :dark="ui.dark"
            @toggleDark="ui.dark = !ui.dark"
          />
        </section>
      </main>
    </div>

    <!-- =========================================================
         ZENTRALER TOAST
         - Alle Views nutzen useToast().toast(...)
         - Nur App.vue rendert toastState
    ========================================================== -->
    <div class="toast" v-if="toastState.open">{{ toastState.text }}</div>
  </div>
</template>

<script setup lang="ts">
/*
  App.vue
  Architektur Entscheidungen
  - Layout/Design über globale CSS Dateien (tokens.css, base.css, layout.css)
  - App.vue enthält KEIN <style scoped>
  - Toast ist zentral (kein Toast Markup in Views)
  - Checks laufen über platform endpoints:
      GET /health
      GET /health/db
    BaseURL kommt aus VITE_API_BASE
*/

import { computed, onMounted, reactive } from "vue";
import { useToast } from "./composables/useToast";
import { platformHealth, platformHealthDb } from "./api/platform";

/* Views */
import AdminTenantsView from "./views/AdminTenantsView.vue";
import AdminAuditView from "./views/AdminAuditView.vue";
import AdminDiagnosticsView from "./views/AdminDiagnosticsView.vue";
import AdminSettingsView from "./views/AdminSettingsView.vue";

/* Zentraler Toast State */
const { toastState, toast } = useToast();

/* Sidebar Sections */
const sections = [
  { id: "kunden", label: "Kunden", icon: "👥" },
  { id: "audit", label: "Audit", icon: "🧾" },
  { id: "diagnostics", label: "Diagnostics", icon: "🩺" },
  { id: "settings", label: "Einstellungen", icon: "⚙️" },
] as const;

type SectionId = (typeof sections)[number]["id"];

/* UI State */
const ui = reactive({
  dark: false,
  actor: "admin",
  adminKey: "",
  section: "kunden" as SectionId,
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
}

/* Titles */
const pageTitle = computed(() => {
  const m: Record<SectionId, string> = {
    kunden: "Kunden",
    audit: "Audit",
    diagnostics: "Diagnostics",
    settings: "Einstellungen",
  };
  return m[ui.section];
});

const pageSubtitle = computed(() => {
  if (ui.section === "kunden") return "Tenants verwalten, aktivieren, Details";
  if (ui.section === "audit") return "Audit Log durchsuchen, filtern, exportieren";
  if (ui.section === "diagnostics") return "Health, Admin Checks, Snapshot";
  return "Security, Theme, Feature Flags";
});

/* Checks */
async function checkApi() {
  api.busy = true;
  try {
    await platformHealth();
    api.ok = true;
    toast("API erreichbar");
  } catch {
    api.ok = false;
    toast("API nicht erreichbar");
  } finally {
    api.busy = false;
  }
}

async function checkDb() {
  db.busy = true;
  try {
    await platformHealthDb();
    db.ok = true;
    toast("DB erreichbar");
  } catch {
    db.ok = false;
    toast("DB nicht erreichbar");
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

/* Boot */
onMounted(async () => {
  await quickRefresh();
});
</script>
