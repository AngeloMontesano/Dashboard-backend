<template>
  <div class="grid1">
    <div class="card">
      <div class="cardHeader">
        <div>
          <div class="cardTitle">Einstellungen</div>
          <div class="cardHint">System, Security, Theme, Feature Flags, Email</div>
        </div>
      </div>

      <div class="box">
        <div v-if="!adminKey" class="alert warn">
          <div class="alertTitle">Admin Key erforderlich</div>
          <div class="alertText">Bitte Admin Key setzen, damit System- und SMTP-Daten geladen werden.</div>
        </div>
        <section class="settingsSection">
          <div class="sectionHeader">
            <div class="sectionTitle">System</div>
            <button class="btnGhost small" @click="toggleSection('system')" :aria-expanded="sectionOpen.system">
              {{ sectionOpen.system ? "Einklappen" : "Aufklappen" }}
            </button>
          </div>
          <div v-if="sectionOpen.system" class="kvGrid">
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
            <button class="btnGhost small" @click="toggleSection('security')" :aria-expanded="sectionOpen.security">
              {{ sectionOpen.security ? "Einklappen" : "Aufklappen" }}
            </button>
          </div>
          <div v-if="sectionOpen.security" class="kvGrid">
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

          <div class="row gap8 wrap" v-if="sectionOpen.security">
            <button class="btnGhost" :disabled="!adminKey && !actor" @click="$emit('resetContext')">
              Admin Context zurücksetzen
            </button>
          </div>
        </section>

        <div class="divider"></div>

        <section class="settingsSection">
          <div class="sectionHeader">
            <div class="sectionTitle">Theme &amp; UI</div>
            <button class="btnGhost small" @click="toggleSection('theme')" :aria-expanded="sectionOpen.theme">
              {{ sectionOpen.theme ? "Einklappen" : "Aufklappen" }}
            </button>
          </div>
          <div v-if="sectionOpen.theme" class="kvGrid">
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
            <div class="sectionTitle">Email / SMTP</div>
            <button class="btnGhost small" @click="toggleSection('email')" :aria-expanded="!sectionCollapsed.email">
              {{ sectionCollapsed.email ? "Aufklappen" : "Einklappen" }}
            </button>
          </div>
          <div v-if="!sectionCollapsed.email" class="kvGrid">
            <div class="kv">
              <div class="k">Host</div>
              <div class="v">
                <input class="input" v-model="smtpSettings.host" :disabled="busy.smtpSave || busy.smtpLoad" placeholder="mail.myitnetwork.de" />
              </div>
            </div>
            <div class="kv">
              <div class="k">Port</div>
              <div class="v">
                <input class="input" type="number" v-model.number="smtpSettings.port" :disabled="busy.smtpSave || busy.smtpLoad" />
              </div>
            </div>
            <div class="kv">
              <div class="k">From</div>
              <div class="v">
                <input class="input" type="email" v-model="smtpSettings.from_email" :disabled="busy.smtpSave || busy.smtpLoad" placeholder="notification@example.com" />
              </div>
            </div>
            <div class="kv">
              <div class="k">User</div>
              <div class="v">
                <input class="input" v-model="smtpSettings.user" :disabled="busy.smtpSave || busy.smtpLoad" placeholder="smtp-user" />
                <div class="muted">Optional, leer lassen falls nicht benötigt.</div>
              </div>
            </div>
            <div class="kv">
              <div class="k">Passwort</div>
              <div class="v">
                <input class="input" type="password" v-model="smtpSettings.password" :disabled="busy.smtpSave || busy.smtpLoad" :placeholder="smtpLoaded.has_password ? '••••••••' : 'Passwort eingeben'" />
                <div class="muted">Leer lassen, um das bestehende Passwort beizubehalten.</div>
              </div>
            </div>
            <div class="kv">
              <div class="k">TLS</div>
              <div class="v">
                <label class="checkboxRow">
                  <input type="checkbox" v-model="smtpSettings.use_tls" :disabled="busy.smtpSave || busy.smtpLoad" />
                  <span>STARTTLS nutzen</span>
                </label>
              </div>
            </div>
            <div class="kv">
              <div class="k">Aktionen</div>
              <div class="v actionsRow">
                <button class="btn" :disabled="busy.smtpSave || busy.smtpLoad" @click="saveEmailSettings">
                  {{ busy.smtpSave ? "Speichert..." : "Speichern" }}
                </button>
                <div class="row gap8 wrap">
                  <input class="input" type="email" v-model="emailTarget" :disabled="busy.smtpTest || busy.smtpLoad" placeholder="test@example.com" />
                  <button class="btnGhost" :disabled="busy.smtpTest || busy.smtpLoad" @click="testEmailSettings">
                    {{ busy.smtpTest ? "Sendet..." : "Test-E-Mail senden" }}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </section>

        <div class="divider"></div>

        <section class="settingsSection">
          <div class="sectionHeader">
            <div class="sectionTitle">Feature Flags (UI)</div>
            <button class="btnGhost small" @click="toggleSection('flags')" :aria-expanded="sectionOpen.flags">
              {{ sectionOpen.flags ? "Einklappen" : "Aufklappen" }}
            </button>
          </div>
          <div v-if="sectionOpen.flags" class="kvGrid">
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
            <div class="sectionTitle">SMTP &amp; Testmail</div>
            <button class="btnGhost small" @click="toggleSection('smtp')" :aria-expanded="sectionOpen.smtp">
              {{ sectionOpen.smtp ? "Einklappen" : "Aufklappen" }}
            </button>
          </div>
          <div v-if="sectionOpen.smtp" class="stack">
            <div class="kvGrid">
              <div class="field">
                <div class="k">Host</div>
                <input class="input" v-model="emailForm.host" :disabled="loadingEmail || savingEmail" placeholder="smtp.example.com" />
              </div>
              <div class="field">
                <div class="k">Port</div>
                <input class="input" type="number" min="1" max="65535" v-model.number="emailForm.port" :disabled="loadingEmail || savingEmail" />
              </div>
              <div class="field">
                <div class="k">From</div>
                <input class="input" v-model="emailForm.from_email" :disabled="loadingEmail || savingEmail" placeholder="no-reply@example.com" />
              </div>
              <div class="field">
                <div class="k">User</div>
                <input class="input" v-model="emailForm.user" :disabled="loadingEmail || savingEmail" placeholder="smtp-user" />
              </div>
              <div class="field">
                <div class="k">Passwort</div>
                <input class="input" type="password" v-model="emailForm.password" :disabled="loadingEmail || savingEmail" placeholder="Neues Passwort (leer = unverändert)" />
                <div class="muted">{{ emailForm.has_password ? "Passwort gesetzt" : "Kein Passwort hinterlegt" }}</div>
              </div>
              <label class="field checkboxRow">
                <input type="checkbox" v-model="emailForm.use_tls" :disabled="loadingEmail || savingEmail" />
                <span>StartTLS verwenden</span>
              </label>
            </div>
            <div class="row gap8 wrap">
              <button class="btnPrimary" :disabled="savingEmail || loadingEmail || !adminKey" @click="saveEmailSettings">
                {{ savingEmail ? "Speichere..." : "Speichern" }}
              </button>
              <div class="muted" v-if="loadingEmail">Lade SMTP Einstellungen…</div>
            </div>
            <div class="divider"></div>
            <div class="kvGrid">
              <div class="field">
                <div class="k">Testmail an</div>
                <input class="input" v-model="testEmail" placeholder="test@example.com" :disabled="testingEmail || savingEmail" />
              </div>
              <div class="field">
                <div class="k">Aktion</div>
                <div class="row gap8 wrap">
                  <button class="btnGhost" :disabled="testingEmail || savingEmail || !testEmail" @click="sendTestEmail">
                    {{ testingEmail ? "Sendet..." : "Testmail senden" }}
                  </button>
                  <div class="muted">Nutzen die aktuell gespeicherten SMTP-Daten.</div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <div class="divider"></div>

        <section class="settingsSection">
          <div class="sectionHeader">
            <div class="sectionTitle">Danger Zone / System Actions</div>
            <button class="btnGhost small" @click="toggleSection('danger')" :aria-expanded="sectionOpen.danger">
              {{ sectionOpen.danger ? "Einklappen" : "Aufklappen" }}
            </button>
          </div>
          <div v-if="sectionOpen.danger" class="kvGrid">
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
import { ref, watch, reactive, computed, withDefaults } from "vue";
import {
  adminGetSystemInfo,
  adminGetSmtpSettings,
  adminUpdateSmtpSettings,
  adminTestSmtpSettings,
} from "../api/admin";
import { useToast } from "../composables/useToast";
import pkg from "../../package.json";
import type {
  AdminSystemInfo,
  SmtpSettingsIn,
  SmtpSettingsOut,
} from "../types";

const props = withDefaults(
  defineProps<{
    apiOk: boolean;
    dbOk: boolean;
    actor?: string;
    adminKey?: string;
    theme?: string;
    apiBase?: string;
    baseDomain?: string;
  }>(),
  {
    actor: "admin",
    adminKey: "",
    theme: "system",
    apiBase: "",
    baseDomain: "",
  }
);

const emit = defineEmits<{
  (e: "setTheme", theme: "light" | "dark" | "system"): void;
  (e: "resetContext"): void;
}>();

const { toast } = useToast();
const sectionOpen = reactive({
  system: true,
  security: true,
  theme: true,
  flags: true,
  smtp: true,
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
type SmtpFormState = {
  host: string;
  port: number | null;
  user: string;
  from_email: string;
  has_password: boolean;
  use_tls: boolean;
  password: string;
};
const emailForm = ref<SmtpFormState>({
  host: "",
  port: 587,
  from_email: "",
  has_password: false,
  use_tls: true,
  password: "",
});
const testEmail = ref("");
const savingEmail = ref(false);
const testingEmail = ref(false);
const loadingEmail = ref(false);

function onThemeChange(themeId: ThemeMode) {
  localTheme.value = themeId;
  emit("setTheme", themeId);
}

function toggleSection(section: keyof typeof sectionOpen) {
  sectionOpen[section] = !sectionOpen[section];
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
      mapEmailSettings({ host: "", port: null, user: "", from_email: "", has_password: false, use_tls: true });
    }
  },
  { immediate: true }
);

function mapEmailSettings(payload: Partial<SmtpSettingsOut>) {
  emailForm.value = {
    host: payload.host || "",
    port: payload.port ?? null,
    user: payload.user || "",
    from_email: payload.from_email || "",
    has_password: payload.has_password ?? false,
    use_tls: payload.use_tls ?? true,
    password: "",
  };
}

async function loadEmailSettings() {
  if (!props.adminKey) {
    mapEmailSettings({ host: "", port: null, user: "", from_email: "", has_password: false, use_tls: true });
    return;
  }
  loadingEmail.value = true;
  try {
    const res = await adminGetSmtpSettings(props.adminKey, props.actor);
    mapEmailSettings(res);
  } catch (e: any) {
    toast(`SMTP Einstellungen laden fehlgeschlagen: ${asError(e)}`, "danger");
  } finally {
    loadingEmail.value = false;
  }
}

async function saveEmailSettings() {
  if (!props.adminKey) return;
  savingEmail.value = true;
  try {
    const payload: SmtpSettingsIn = {
      host: emailForm.value.host.trim(),
      port: Number(emailForm.value.port || 0),
      from_email: emailForm.value.from_email.trim(),
      user: emailForm.value.user?.trim() || null,
      password: emailForm.value.password ? emailForm.value.password : undefined,
      use_tls: Boolean(emailForm.value.use_tls),
    };
    const res = await adminUpdateSmtpSettings(props.adminKey, props.actor, payload);
    mapEmailSettings(res);
    toast("SMTP Einstellungen gespeichert", "success");
  } catch (e: any) {
    toast(`SMTP Einstellungen speichern fehlgeschlagen: ${asError(e)}`, "danger");
  } finally {
    savingEmail.value = false;
    emailForm.value.password = "";
  }
}

async function sendTestEmail() {
  if (!props.adminKey || !testEmail.value.trim()) return;
  testingEmail.value = true;
  try {
    const res = await adminTestSmtpSettings(props.adminKey, props.actor, testEmail.value.trim());
    if (res.ok) {
      toast(`Testmail gesendet (${res.request_id || "ohne request_id"})`, "success");
    } else {
      toast(`Testmail fehlgeschlagen: ${res.detail || "Unbekannter Fehler"}`, "danger");
    }
  } catch (e: any) {
    toast(`Testmail fehlgeschlagen: ${asError(e)}`, "danger");
  } finally {
    testingEmail.value = false;
  }
}
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

.settingsSection{
  display: grid;
  gap: 12px;
}

.sectionHeader{
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.checkboxRow{
  display: inline-flex;
  gap: 8px;
  align-items: center;
}

.alert{
  border: 1px solid var(--border);
  background: var(--surface2);
  border-radius: var(--radius2);
  padding: 10px 12px;
  margin-bottom: 12px;
}
.alert.warn{
  border-color: var(--orange-500, #f59e0b);
}
.alertTitle{
  font-weight: 600;
}
.alertText{
  color: var(--muted);
  font-size: 13px;
}
</style>
