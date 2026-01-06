<template>
  <div class="grid1">
    <div class="card">
      <div class="cardHeader">
        <div>
          <div class="cardTitle">Einstellungen</div>
          <div class="cardHint">System, Security, Theme, Feature Flags, Email</div>
        </div>
      </div>

      <div class="stack">
        <div class="collapsible">
          <div class="collapsibleHeader">
            <div>
              <div class="sectionTitle">System</div>
              <div class="sectionHint">System, Security Themes, Feature Flags</div>
            </div>
            <button class="btnGhost small" type="button" @click="toggleSection('system')">
              {{ openSections.system ? "Einklappen" : "Ausklappen" }}
            </button>
          </div>
          <div v-if="openSections.system" class="kvGrid">
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
        </div>

        <div class="collapsible">
          <div class="collapsibleHeader">
            <div class="sectionTitle">Security &amp; Auth</div>
            <button class="btnGhost small" type="button" @click="toggleSection('security')">
              {{ openSections.security ? "Einklappen" : "Ausklappen" }}
            </button>
          </div>
          <div v-if="openSections.security" class="kvGrid">
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
            <div class="row gap8 wrap">
              <button class="btnGhost" :disabled="!adminKey && !actor" @click="$emit('resetContext')">
                Admin Context zurücksetzen
              </button>
            </div>
          </div>
        </div>

        <div class="collapsible">
          <div class="collapsibleHeader">
            <div class="sectionTitle">Theme &amp; UI</div>
            <button class="btnGhost small" type="button" @click="toggleSection('theme')">
              {{ openSections.theme ? "Einklappen" : "Ausklappen" }}
            </button>
          </div>
          <div v-if="openSections.theme" class="kvGrid">
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
        </div>

        <div class="collapsible">
          <div class="collapsibleHeader">
            <div class="sectionTitle">Feature Flags (UI)</div>
            <button class="btnGhost small" type="button" @click="toggleSection('flags')">
              {{ openSections.flags ? "Einklappen" : "Ausklappen" }}
            </button>
          </div>
          <div v-if="openSections.flags" class="kvGrid">
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
        </div>

        <div class="collapsible">
          <div class="collapsibleHeader">
            <div class="sectionTitle">Email</div>
            <button class="btnGhost small" type="button" @click="toggleSection('email')">
              {{ openSections.email ? "Einklappen" : "Ausklappen" }}
            </button>
          </div>
          <div v-if="openSections.email" class="stack">
            <div class="fieldGrid">
              <label class="field">
                <div class="k">SMTP Host</div>
                <input class="input" v-model.trim="emailForm.host" placeholder="smtp.example.com" />
              </label>
              <label class="field">
                <div class="k">Port</div>
                <input class="input" v-model.number="emailForm.port" type="number" min="1" max="65535" placeholder="587" />
              </label>
              <label class="field">
                <div class="k">From</div>
                <input class="input" v-model.trim="emailForm.from_email" type="email" placeholder="notification@example.com" />
              </label>
              <label class="field">
                <div class="k">User</div>
                <input class="input" v-model.trim="emailForm.user" placeholder="smtp-user (optional)" />
              </label>
              <label class="field">
                <div class="k">Passwort</div>
                <input
                  class="input"
                  v-model="emailForm.password"
                  type="password"
                  placeholder="Neues Passwort (leer lassen um zu behalten)"
                />
                <div class="muted" v-if="emailForm.has_password">Gespeichertes Passwort bleibt erhalten wenn leer.</div>
              </label>
            </div>
            <div class="row gap8 wrap">
              <button class="btnPrimary" type="button" :disabled="!adminKey || savingEmail" @click="saveEmailSettings">
                {{ savingEmail ? "Speichern..." : "Speichern" }}
              </button>
              <button class="btnGhost" type="button" :disabled="savingEmail" @click="loadEmailSettings">
                Neu laden
              </button>
            </div>
            <div class="divider"></div>
            <div class="fieldGrid">
              <label class="field">
                <div class="k">Test-E-Mail Empfänger</div>
                <input class="input" v-model.trim="testEmail" type="email" placeholder="you@example.com" />
              </label>
              <div class="field">
                <div class="k">&nbsp;</div>
                <button class="btnGhost" type="button" :disabled="!testEmail || testingEmail" @click="sendTestEmail">
                  {{ testingEmail ? "Sende..." : "Test senden" }}
                </button>
              </div>
            </div>
          </div>
        </div>

        <div class="collapsible">
          <div class="collapsibleHeader">
            <div class="sectionTitle">Danger Zone / System Actions</div>
            <button class="btnGhost small" type="button" @click="toggleSection('danger')">
              {{ openSections.danger ? "Einklappen" : "Ausklappen" }}
            </button>
          </div>
          <div v-if="openSections.danger" class="kvGrid">
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
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/*
  AdminSettingsView
  - Systemweite Einstellungen, Security-Hinweise, Theme & Flags
*/
import { ref, watch } from "vue";
import { adminGetSystemInfo, adminGetEmailSettings, adminUpdateEmailSettings, adminTestEmail } from "../api/admin";
import { useToast } from "../composables/useToast";
import pkg from "../../package.json";
import type { AdminSystemInfo, SystemEmailSettings, SystemEmailSettingsUpdate } from "../types";

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
const themes = [
  { id: "system", label: "System" },
  { id: "light", label: "Light" },
  { id: "dark", label: "Dark" },
];
const localTheme = ref((props.theme as "light" | "dark" | "system") || "system");
const grafanaUrl = import.meta.env.VITE_GRAFANA_URL || "http://localhost:3000";
const buildInfo = (import.meta.env.VITE_BUILD_INFO as string | undefined) || pkg.version;
const systemInfo = ref<AdminSystemInfo | null>(null);
const openSections = ref<Record<string, boolean>>({
  system: true,
  security: true,
  theme: true,
  flags: true,
  email: true,
  danger: false,
});
const emailForm = ref<SystemEmailSettings & { password: string }>({
  host: "",
  port: null,
  user: "",
  from_email: "",
  has_password: false,
  password: "",
});
const testEmail = ref("");
const savingEmail = ref(false);
const testingEmail = ref(false);

function onThemeChange(themeId: "light" | "dark" | "system") {
  localTheme.value = themeId;
  emit("setTheme", themeId);
}

function toggleSection(section: keyof typeof openSections.value) {
  openSections.value[section] = !openSections.value[section];
}

function mapEmailSettings(data: SystemEmailSettings) {
  emailForm.value.host = data.host || "";
  emailForm.value.port = data.port ?? null;
  emailForm.value.user = data.user || "";
  emailForm.value.from_email = data.from_email || "";
  emailForm.value.has_password = data.has_password;
  emailForm.value.password = "";
}

async function loadEmailSettings() {
  if (!props.adminKey) {
    mapEmailSettings({ host: "", port: null, user: "", from_email: "", has_password: false });
    return;
  }
  try {
    const res = await adminGetEmailSettings(props.adminKey, props.actor);
    mapEmailSettings(res);
  } catch (e: any) {
    toast(`E-Mail Einstellungen laden fehlgeschlagen: ${asError(e)}`, "danger");
  }
}

async function saveEmailSettings() {
  if (!props.adminKey) return;
  savingEmail.value = true;
  try {
    const payload: SystemEmailSettingsUpdate = {
      host: emailForm.value.host || null,
      port: emailForm.value.port ?? null,
      user: emailForm.value.user || null,
      from_email: emailForm.value.from_email || null,
      password: emailForm.value.password ? emailForm.value.password : null,
    };
    const res = await adminUpdateEmailSettings(props.adminKey, props.actor, payload);
    mapEmailSettings(res);
    toast("E-Mail Einstellungen gespeichert", "success");
  } catch (e: any) {
    toast(`Speichern fehlgeschlagen: ${asError(e)}`, "danger");
  } finally {
    savingEmail.value = false;
  }
}

async function sendTestEmail() {
  if (!props.adminKey || !testEmail.value) return;
  testingEmail.value = true;
  try {
    const res = await adminTestEmail(props.adminKey, props.actor, testEmail.value);
    toast(res.detail || "Test-E-Mail gesendet", res.performed ? "success" : "danger");
  } catch (e: any) {
    toast(`Test-E-Mail fehlgeschlagen: ${asError(e)}`, "danger");
  } finally {
    testingEmail.value = false;
  }
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
      loadEmailSettings();
    }
    if (!key) {
      systemInfo.value = null;
      mapEmailSettings({ host: "", port: null, user: "", from_email: "", has_password: false });
    }
  },
  { immediate: true }
);
</script>

<style scoped>
.stack{
  display: grid;
  gap: 12px;
}
.collapsible{
  border: 1px solid var(--border);
  border-radius: var(--radius2);
  background: var(--surface2);
  padding: 12px;
  box-shadow: var(--shadow);
}
.collapsibleHeader{
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: 8px;
}
.sectionHint{
  color: var(--muted);
  font-size: 12px;
}
.fieldGrid{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 10px;
}
.field .k{
  margin-bottom: 4px;
}
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
</style>
