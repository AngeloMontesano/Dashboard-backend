<template>
  <div class="grid1">
    <div class="card">
      <div class="cardHeader">
        <div>
          <div class="cardTitle">Einstellungen</div>
          <div class="cardHint">Security, Feature Flags</div>
        </div>
      </div>

      <div class="box">
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
            <div class="k">Admin Key Länge</div>
            <div class="v">{{ adminKey ? adminKey.length : 0 }} Zeichen</div>
          </div>
          <div class="kv">
            <div class="k">Actor</div>
            <div class="v mono">{{ actor || "admin" }}</div>
          </div>
        </div>

        <div class="divider"></div>

        <div class="row gap8 wrap">
          <button class="btnGhost" @click="$emit('toggleDark')">
            {{ dark ? "Light Mode" : "Dark Mode" }}
          </button>
          <button class="btnGhost" :disabled="!adminKey && !actor" @click="$emit('resetContext')">
            Admin Context zurücksetzen
          </button>
        </div>

        <div class="divider"></div>

        <div class="kvGrid">
          <div class="kv">
            <div class="k">Security Hinweise</div>
            <div class="v">
              <ul class="bullets">
                <li>Admin Key nie im LocalStorage persistieren.</li>
                <li>Nur HTTPS nutzen, wenn hinter Proxy.</li>
                <li>Actor optional für Audit setzen (X-Admin-Actor).</li>
              </ul>
            </div>
          </div>
          <div class="kv">
            <div class="k">Feature Flags (UI)</div>
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
    </div>
  </div>
</template>

<script setup lang="ts">
/*
  AdminSettingsView
  - Phase 1: Platzhalter
  - Phase 2: UI Settings, Feature Flags
*/
defineProps<{
  apiOk: boolean;
  dbOk: boolean;
  actor: string;
  adminKey: string;
  dark: boolean;
  apiBase: string;
  baseDomain: string;
}>();

defineEmits<{
  (e: "toggleDark"): void;
  (e: "resetContext"): void;
}>();
</script>
