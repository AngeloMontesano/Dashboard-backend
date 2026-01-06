<template>
  <div class="grid1">
    <div class="card">
      <div class="cardHeader">
        <div>
          <div class="cardTitle">Einstellungen</div>
          <div class="cardHint">System, Security, Theme, Feature Flags</div>
        </div>
      </div>

      <div class="box">
        <section class="settingsSection">
          <div class="sectionHeader">
            <div class="sectionTitle">System</div>
            <button class="btnGhost small" @click="toggleSection('system')" :aria-expanded="!sectionCollapsed.system">
              {{ sectionCollapsed.system ? "Aufklappen" : "Einklappen" }}
            </button>
          </div>
          <div v-if="!sectionCollapsed.system" class="kvGrid">
            <div class="kv">
              <div class="k">API Base</div>
              <div class="v mono">{{ apiBase }}</div>
            </div>
            <div class="kv">
              <div class="k">Base Domain</div>
              <div class="v mono">{{ baseDomain }}</div>
            </div>
            <div class="kv">
              <div class="k">Observability</div>
              <div class="v">
                <a :href="grafanaUrl" target="_blank" rel="noreferrer">Grafana</a>
                <div class="muted">Prometheus &amp; Loki</div>
              </div>
            </div>
            <div class="kv">
              <div class="k">Health</div>
              <div class="v pill-row">
                <span class="tag" :class="apiOk ? 'ok' : 'bad'">API {{ apiOk ? "ok" : "down" }}</span>
                <span class="tag" :class="dbOk ? 'ok' : 'bad'">DB {{ dbOk ? "ok" : "down" }}</span>
              </div>
            </div>
            <div class="kv">
              <div class="k">Build Info</div>
              <div class="v">
                <div class="mono">{{ buildInfo }}</div>
                <div class="muted">App Version (UI)</div>
              </div>
            </div>
            <div class="kv">
              <div class="k">Backend Build</div>
              <div class="v">
                <div v-if="systemInfo">
                  <div class="mono">{{ systemInfo.git_commit || "unknown" }}</div>
                  <div class="muted">Branch: {{ systemInfo.build_branch || "unknown" }}</div>
                  <div class="muted">Build: {{ systemInfo.build_timestamp || "unknown" }}</div>
                  <div class="muted">App: {{ systemInfo.app_version }} · {{ systemInfo.environment }}</div>
                  <div class="muted" v-if="systemInfo.image_tag">Image: {{ systemInfo.image_tag }}</div>
                  <div class="muted">DB Status: {{ systemInfo.db }}</div>
                  <div v-if="systemInfo.db_error" class="errorText">DB Fehler: {{ systemInfo.db_error }}</div>
                </div>
                <div v-else class="muted">noch nicht geladen</div>
              </div>
            </div>
          </div>
        </section>

        <div class="divider"></div>

        <section class="settingsSection">
          <div class="sectionHeader">
            <div class="sectionTitle">Security &amp; Auth</div>
            <button class="btnGhost small" @click="toggleSection('security')" :aria-expanded="!sectionCollapsed.security">
              {{ sectionCollapsed.security ? "Aufklappen" : "Einklappen" }}
            </button>
          </div>
          <div v-if="!sectionCollapsed.security" class="kvGrid">
            <div class="kv">
              <div class="k">Admin Key Länge</div>
              <div class="v">{{ adminKey ? adminKey.length : 0 }} Zeichen</div>
            </div>
            <div class="kv">
              <div class="k">Actor</div>
              <div class="v mono">{{ actor || "admin" }}</div>
            </div>
            <div class="kv">
              <div class="k">Hinweise</div>
              <div class="v">
                <ul class="bullets">
                  <li>Admin Key nie im LocalStorage persistieren.</li>
                  <li>Nur HTTPS nutzen, wenn hinter Proxy.</li>
                  <li>Actor optional für Audit setzen (X-Admin-Actor).</li>
                </ul>
              </div>
            </div>
          </div>

          <div class="row gap8 wrap" v-if="!sectionCollapsed.security">
            <button class="btnGhost" :disabled="!adminKey && !actor" @click="$emit('resetContext')">
              Admin Context zurücksetzen
            </button>
          </div>
        </section>

        <div class="divider"></div>

        <section class="settingsSection">
          <div class="sectionHeader">
            <div class="sectionTitle">Theme &amp; UI</div>
            <button class="btnGhost small" @click="toggleSection('theme')" :aria-expanded="!sectionCollapsed.theme">
              {{ sectionCollapsed.theme ? "Aufklappen" : "Einklappen" }}
            </button>
          </div>
          <div v-if="!sectionCollapsed.theme" class="kvGrid">
            <div class="kv">
              <div class="k">Theme</div>
              <div class="v">
                <div class="row gap8 wrap themeSelector">
                  <label v-for="t in themes" :key="t.id" class="themeOption">
                    <input type="radio" :value="t.id" v-model="localTheme" @change="onThemeChange(t.id)" />
                    <span>{{ t.label }}</span>
                  </label>
                </div>
                <div class="muted">Wirken direkt im UI (ohne Reload).</div>
              </div>
            </div>
          </div>
        </section>

        <div class="divider"></div>

        <section class="settingsSection">
          <div class="sectionHeader">
            <div class="sectionTitle">Feature Flags (UI)</div>
            <button class="btnGhost small" @click="toggleSection('flags')" :aria-expanded="!sectionCollapsed.flags">
              {{ sectionCollapsed.flags ? "Aufklappen" : "Einklappen" }}
            </button>
          </div>
          <div v-if="!sectionCollapsed.flags" class="kvGrid">
            <div class="kv">
              <div class="v">
                <ul class="bullets">
                  <li>Dark Mode Toggle</li>
                  <li>Admin Context Reset</li>
                  <li>Health-Anzeigen in Sidebar</li>
                </ul>
              </div>
            </div>
          </div>
        </section>

        <div class="divider"></div>

        <section class="settingsSection">
          <div class="sectionHeader">
            <div class="sectionTitle">Danger Zone / System Actions</div>
            <button class="btnGhost small" @click="toggleSection('danger')" :aria-expanded="!sectionCollapsed.danger">
              {{ sectionCollapsed.danger ? "Aufklappen" : "Einklappen" }}
            </button>
          </div>
          <div v-if="!sectionCollapsed.danger" class="kvGrid">
            <div class="kv">
              <div class="k">Cache / Reindex</div>
              <div class="v">
                <div class="muted">Nicht unterstützt in diesem Deployment.</div>
                <div class="muted">Kein Cache/Search konfiguriert.</div>
              </div>
            </div>
            <div class="kv">
              <div class="k">System Restart</div>
              <div class="v">
                <div class="muted">Restart erfolgt außerhalb der Anwendung (Docker/Portainer).</div>
                <div class="muted">Kein API-gestützter Restart konfiguriert.</div>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/*
  AdminSettingsView
  - Systemweite Einstellungen, Security-Hinweise, Theme & Flags
*/
import { computed, ref, watch } from "vue";
import { adminGetSystemInfo } from "../api/admin";
import { useToast } from "../composables/useToast";
import pkg from "../../package.json";
import type { AdminSystemInfo } from "../types";

type ThemeMode = "light" | "dark" | "system";

const props = defineProps<{
  apiOk: boolean;
  dbOk: boolean;
  actor: string;
  adminKey: string;
  theme: string;
  apiBase: string;
  baseDomain: string;
}>();

const emit = defineEmits<{
  (e: "setTheme", theme: "light" | "dark" | "system"): void;
  (e: "resetContext"): void;
}>();

const { toast } = useToast();
const sectionCollapsed = ref({
  system: true,
  security: true,
  theme: true,
  flags: true,
  danger: true,
});
const themes = [
  { id: "system", label: "System" },
  { id: "light", label: "Light" },
  { id: "dark", label: "Dark" },
];
const safeTheme = computed<ThemeMode>(() => (props.theme as ThemeMode) || "system");
const localTheme = ref<ThemeMode>(safeTheme.value);
const grafanaUrl = import.meta.env.VITE_GRAFANA_URL || "http://localhost:3000";
const buildInfo = (import.meta.env.VITE_BUILD_INFO as string | undefined) || pkg.version;
const systemInfo = ref<AdminSystemInfo | null>(null);

function onThemeChange(themeId: ThemeMode) {
  localTheme.value = themeId;
  emit("setTheme", themeId);
}

function toggleSection(section: keyof typeof sectionCollapsed.value) {
  sectionCollapsed.value = {
    ...sectionCollapsed.value,
    [section]: !sectionCollapsed.value[section],
  };
}

async function loadSystemInfo() {
  if (!props.adminKey) {
    systemInfo.value = null;
    return;
  }
  try {
    systemInfo.value = await adminGetSystemInfo(props.adminKey, props.actor);
  } catch (e: any) {
    toast(`System Info fehlgeschlagen: ${asError(e)}`, "danger");
    systemInfo.value = null;
  }
}

function asError(e: any): string {
  if (!e) return "unknown";
  if (typeof e === "string") return e;
  if (e?.response?.data?.detail) return JSON.stringify(e.response.data.detail);
  if (e?.message) return e.message;
  try {
    return JSON.stringify(e);
  } catch {
    return String(e);
  }
}

watch(
  () => props.adminKey,
  (key, prev) => {
    if (key && key !== prev) {
      loadSystemInfo();
    }
    if (!key) {
      systemInfo.value = null;
    }
  },
  { immediate: true }
);

watch(
  () => props.theme,
  (value) => {
    const normalized = (value as ThemeMode) || "system";
    localTheme.value = normalized;
  },
  { immediate: true }
);

// Placeholder: the settings view no longer uses email settings directly, but keep the hook defined
// to avoid runtime ReferenceErrors if legacy watchers/handlers fire.
function loadEmailSettings() {
  return;
}
</script>

<style scoped>
.themeSelector{
  display: flex;
  gap: 12px;
}
.themeOption{
  display: inline-flex;
  gap: 6px;
  align-items: center;
  padding: 6px 10px;
  border: 1px solid var(--border);
  border-radius: var(--radius2);
  background: var(--surface);
  cursor: pointer;
}
.themeOption input{
  margin: 0;
}

.settingsSection{
  display: grid;
  gap: 12px;
}

.sectionHeader{
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
