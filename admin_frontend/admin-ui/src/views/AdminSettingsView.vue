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
        <div class="sectionTitle">System</div>
        <div class="kvGrid">
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
            <div class="v muted">nicht verfügbar – Backend-Endpoint für Build/Commit fehlt.</div>
          </div>
        </div>

        <div class="divider"></div>

        <div class="sectionTitle">Security &amp; Auth</div>
        <div class="kvGrid">
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

        <div class="row gap8 wrap">
          <button class="btnGhost" :disabled="!adminKey && !actor" @click="$emit('resetContext')">
            Admin Context zurücksetzen
          </button>
        </div>

        <div class="divider"></div>

        <div class="sectionTitle">Theme &amp; UI</div>
        <div class="kvGrid">
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

        <div class="divider"></div>

        <div class="sectionTitle">Feature Flags (UI)</div>
        <div class="kvGrid">
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

        <div class="divider"></div>

        <div class="sectionTitle">Danger Zone / System Actions</div>
        <div class="kvGrid">
          <div class="kv">
            <div class="k">Cache / Reindex</div>
            <div class="v muted">Endpoint fehlt – nur Anzeige, keine Aktion verfügbar (siehe TODO).</div>
          </div>
          <div class="kv">
            <div class="k">System Restart</div>
            <div class="v muted">Kein Admin-Endpoint vorhanden; Operation muss serverseitig bereitgestellt werden.</div>
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
import { ref } from "vue";
import pkg from "../../package.json";

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

const themes = [
  { id: "system", label: "System" },
  { id: "light", label: "Light" },
  { id: "dark", label: "Dark" },
];
const localTheme = ref((props.theme as "light" | "dark" | "system") || "system");
const grafanaUrl = import.meta.env.VITE_GRAFANA_URL || "http://localhost:3000";
const buildInfo = (import.meta.env.VITE_BUILD_INFO as string | undefined) || pkg.version;

function onThemeChange(themeId: "light" | "dark" | "system") {
  localTheme.value = themeId;
  emit("setTheme", themeId);
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
</style>
