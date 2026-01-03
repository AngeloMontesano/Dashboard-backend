<template>
  <!-- Kunden Section -->
  <div class="grid2">
    <!-- Left Card: Tenants -->
    <div class="card">
      <div class="cardHeader">
        <div>
          <div class="cardTitle">Kunden</div>
          <div class="cardHint">Tenants auswählen und verwalten</div>
        </div>
        <div class="cardHeaderActions">
          <button class="btnGhost" @click="openCreateTenant">Tenant anlegen</button>
        </div>
      </div>

      <div class="controls">
        <input class="input" v-model.trim="tenantQuery" placeholder="Suche nach Name, Slug, ID" />
        <select class="input" v-model="tenantFilter">
          <option value="all">Alle</option>
          <option value="active">Aktiv</option>
          <option value="disabled">Deaktiviert</option>
        </select>
      </div>

      <div class="meta">
        <div class="muted">Treffer: {{ filteredTenants.length }}</div>
        <div class="muted">Ausgewählt: {{ selectedTenant ? selectedTenant.slug : "keiner" }}</div>
      </div>

      <div class="tableWrap">
        <table class="table">
          <thead>
            <tr>
              <th>Slug</th>
              <th>Name</th>
              <th>Status</th>
              <th class="right">Aktionen</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="t in filteredTenants"
              :key="t.id"
              :class="{ rowActive: selectedTenant?.id === t.id }"
              @click="selectTenant(t)"
            >
              <td class="mono">{{ t.slug }}</td>
              <td>{{ t.name }}</td>
              <td>
                <span class="tag" :class="t.active ? 'ok' : 'bad'">
                  {{ t.active ? "aktiv" : "deaktiviert" }}
                </span>
              </td>
              <td class="right">
                <button class="link" @click.stop="openTenantDrawer(t)">Details</button>
                <button class="link" @click.stop="toggleTenant(t)">
                  {{ t.active ? "deaktivieren" : "aktivieren" }}
                </button>
              </td>
            </tr>

            <tr v-if="filteredTenants.length === 0">
              <td colspan="4" class="mutedPad">Keine Tenants gefunden.</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="hintBox">
        Hinweis: Suche ist Demo. Später: API Suche und Pagination.
      </div>
    </div>

    <!-- Right Card: Kunden Workspace -->
    <div class="card">
      <div class="cardHeader">
        <div>
          <div class="cardTitle">Workspace</div>
          <div class="cardHint">Kundenbezogene Funktionen</div>
        </div>
        <div class="cardHeaderActions">
          <button class="btnGhost" @click="copyDiagnostics">Snapshot kopieren</button>
        </div>
      </div>

      <div class="tabs">
        <button
          v-for="t in kundenTabs"
          :key="t.id"
          class="tab"
          :class="{ active: tab === t.id }"
          @click="tab = t.id"
        >
          {{ t.label }}
        </button>
      </div>

      <div class="panel" v-if="tab === 'kunden.uebersicht'">
        <div class="kpis">
          <div class="kpi">
            <div class="kpiLabel">Aktive Tenants</div>
            <div class="kpiValue">{{ tenants.filter(x => x.active).length }}</div>
          </div>
          <div class="kpi">
            <div class="kpiLabel">Benutzer (Demo)</div>
            <div class="kpiValue">{{ demoUsers.length }}</div>
          </div>
          <div class="kpi">
            <div class="kpiLabel">Letzte Audits (Demo)</div>
            <div class="kpiValue">{{ demoAudits.length }}</div>
          </div>
          <div class="kpi">
            <div class="kpiLabel">API Status</div>
            <div class="kpiValue">{{ apiOk ? "ok" : "down" }}</div>
          </div>
        </div>

        <div class="sectionTitle">Ausgewählter Tenant</div>
        <div class="box">
          <div v-if="!selectedTenant" class="muted">Kein Tenant ausgewählt.</div>

          <div v-else class="kvGrid">
            <div class="kv">
              <div class="k">Name</div>
              <div class="v">{{ selectedTenant.name }}</div>
            </div>
            <div class="kv">
              <div class="k">Slug</div>
              <div class="v mono">{{ selectedTenant.slug }}</div>
            </div>
            <div class="kv">
              <div class="k">Status</div>
              <div class="v">
                <span class="tag" :class="selectedTenant.active ? 'ok' : 'bad'">
                  {{ selectedTenant.active ? "aktiv" : "deaktiviert" }}
                </span>
              </div>
            </div>
            <div class="kv">
              <div class="k">Tenant ID</div>
              <div class="v mono">{{ selectedTenant.id }}</div>
            </div>
          </div>
        </div>
      </div>

      <div class="panel" v-else-if="tab === 'kunden.benutzer'">
        <div class="sectionTitle">Benutzer (Demo)</div>
        <div class="box">
          <div class="tableWrap">
            <table class="table">
              <thead>
                <tr>
                  <th>Email</th>
                  <th>Rolle</th>
                  <th>Status</th>
                  <th class="right">Aktionen</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="u in demoUsers" :key="u.id">
                  <td>{{ u.email }}</td>
                  <td><span class="tag neutral">{{ u.role }}</span></td>
                  <td>
                    <span class="tag" :class="u.active ? 'ok' : 'bad'">
                      {{ u.active ? "aktiv" : "gesperrt" }}
                    </span>
                  </td>
                  <td class="right">
                    <button class="link" @click="toast('Passwort Reset (Demo)')">Reset</button>
                    <button class="link" @click="toast('Audit öffnen (Demo)')">Audit</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="hintBox" style="margin-top: 10px;">
            Später: Users tenant scoped laden, Reset über Admin Endpoint.
          </div>
        </div>
      </div>

      <div class="panel" v-else-if="tab === 'kunden.memberships'">
        <div class="sectionTitle">Memberships (Demo)</div>
        <div class="box">
          <div class="muted">
            Später: Admin Memberships API nutzen.
          </div>

          <div class="pillRow" style="margin-top: 10px;">
            <span class="tag neutral">owner</span>
            <span class="tag neutral">admin</span>
            <span class="tag neutral">worker</span>
            <span class="tag neutral">sales</span>
          </div>
        </div>
      </div>

      <div class="panel" v-else>
        <div class="sectionTitle">Support Sessions (Demo)</div>
        <div class="box">
          <div class="muted">
            Später: Support Sessions pro Tenant.
          </div>

          <div class="rowActions" style="margin-top: 12px;">
            <button class="btnPrimary" @click="toast('Support Session erzeugt (Demo)')">Code erzeugen</button>
            <button class="btnGhost" @click="toast('Session beendet (Demo)')">Beenden</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Drawer -->
    <div v-if="drawer.open" class="backdrop" @click="closeDrawer"></div>
    <aside v-if="drawer.open" class="drawer">
      <div class="drawerHeader">
        <div>
          <div class="drawerTitle">{{ drawer.tenant?.name }}</div>
          <div class="drawerSub mono">{{ drawer.tenant?.slug }} · {{ drawer.tenant?.id }}</div>
        </div>
        <button class="btnGhost" @click="closeDrawer">Schließen</button>
      </div>

      <div class="drawerBody">
        <div class="sectionTitle">Aktionen</div>
        <div class="rowActions">
          <button class="btnPrimary" @click="toggleTenant(drawer.tenant)">
            {{ drawer.tenant?.active ? "Deaktivieren" : "Aktivieren" }}
          </button>
          <button class="btnGhost" @click="toast('Support Session (Demo)')">Support Session</button>
          <button class="btnGhost" @click="toast('Reset (Demo)')">Passwort Reset</button>
        </div>

        <div class="sectionTitle" style="margin-top: 12px;">Notiz</div>
        <textarea class="input area" v-model="drawer.note" placeholder="Interne Notiz"></textarea>
      </div>
    </aside>

    <!-- Modal -->
    <div v-if="modal.open" class="backdrop" @click="modal.open = false"></div>
    <div v-if="modal.open" class="modal">
      <div class="modalHeader">
        <div class="modalTitle">Tenant anlegen</div>
        <button class="btnGhost" @click="modal.open = false">Schließen</button>
      </div>

      <div class="modalBody">
        <div class="formGrid">
          <div class="field">
            <div class="label">Name</div>
            <input class="input" v-model.trim="modal.name" placeholder="Bäckerei Muster" />
          </div>
          <div class="field">
            <div class="label">Slug</div>
            <input class="input" v-model.trim="modal.slug" placeholder="baeckerei-muster" />
          </div>
        </div>
        <div class="muted" style="margin-top: 10px;">Demo: wird lokal erzeugt.</div>
      </div>

      <div class="modalFooter">
        <button class="btnGhost" @click="modal.open = false">Abbrechen</button>
        <button class="btnPrimary" @click="createTenant">Anlegen</button>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
/*
  KundenView
  Zweck
  - Enthält nur Kunden Section UI und State
  - App.vue bleibt Shell plus Navigation

  Später
  - Demo Daten durch echte API Calls ersetzen
*/

import { computed, reactive, ref } from "vue";
import { useToast } from "../composables/useToast";

type Tenant = { id: string; slug: string; name: string; active: boolean };

const props = defineProps<{
  apiOk: boolean;
}>();

const { toast } = useToast();

/* Tabs */
const kundenTabs = [
  { id: "kunden.uebersicht", label: "Übersicht" },
  { id: "kunden.benutzer", label: "Benutzer" },
  { id: "kunden.memberships", label: "Memberships" },
  { id: "kunden.support", label: "Support" },
];

const tab = ref<string>("kunden.uebersicht");

/* Demo Data */
const tenants = ref<Tenant[]>([
  { id: "t_01HZZ1A", slug: "kunde1", name: "Bäckerei Sonnenschein", active: true },
  { id: "t_01HZZ1B", slug: "kunde2", name: "Eiswerk Nord", active: true },
  { id: "t_01HZZ1C", slug: "kunde3", name: "Café Am Markt", active: false },
  { id: "t_01HZZ1D", slug: "kunde4", name: "Pasticceria Milano", active: true },
]);

const tenantQuery = ref<string>("");
const tenantFilter = ref<string>("all");
const selectedTenant = ref<Tenant | null>(null);

const filteredTenants = computed(() => {
  const q = tenantQuery.value.toLowerCase();

  return tenants.value
    .filter((t) => {
      if (tenantFilter.value === "active") return t.active;
      if (tenantFilter.value === "disabled") return !t.active;
      return true;
    })
    .filter((t) => {
      if (!q) return true;
      return (
        t.slug.toLowerCase().includes(q) ||
        t.name.toLowerCase().includes(q) ||
        t.id.toLowerCase().includes(q)
      );
    });
});

function selectTenant(t: Tenant) {
  selectedTenant.value = t;
}

function toggleTenant(t?: Tenant | null) {
  if (!t) return;
  t.active = !t.active;
  toast(t.active ? "Tenant aktiviert" : "Tenant deaktiviert");
}

/* Drawer */
const drawer = reactive<{ open: boolean; tenant: Tenant | null; note: string }>({
  open: false,
  tenant: null,
  note: "",
});

function openTenantDrawer(t: Tenant) {
  drawer.open = true;
  drawer.tenant = t;
  drawer.note = "";
}

function closeDrawer() {
  drawer.open = false;
  drawer.tenant = null;
  drawer.note = "";
}

/* Modal */
const modal = reactive<{ open: boolean; name: string; slug: string }>({
  open: false,
  name: "",
  slug: "",
});

function openCreateTenant() {
  modal.open = true;
  modal.name = "";
  modal.slug = "";
}

function createTenant() {
  const name = modal.name.trim();
  const slug = modal.slug.trim();

  if (!name || !slug) {
    toast("Name und Slug sind Pflicht");
    return;
  }

  tenants.value.unshift({
    id: `t_${Math.random().toString(16).slice(2, 9).toUpperCase()}`,
    slug,
    name,
    active: true,
  });

  modal.open = false;
  toast("Tenant angelegt");
}

/* Diagnostics Snapshot */
const demoAudits = [
  { id: "a1", ts: "2026-01-02 10:12", title: "Tenant created", meta: "actor=admin, tenant=kunde4" },
  { id: "a2", ts: "2026-01-02 10:44", title: "User password reset", meta: "actor=admin, user=verkauf@kunde1.de" },
  { id: "a3", ts: "2026-01-02 11:07", title: "Tenant disabled", meta: "actor=admin, tenant=kunde3" },
];

const demoUsers = [
  { id: "u1", email: "admin@kunde1.de", role: "owner", active: true },
  { id: "u2", email: "lager@kunde1.de", role: "worker", active: true },
  { id: "u3", email: "verkauf@kunde1.de", role: "sales", active: false },
];

const diagnostics = computed(() => ({
  apiOk: props.apiOk,
  selectedTenant: selectedTenant.value
    ? { id: selectedTenant.value.id, slug: selectedTenant.value.slug, active: selectedTenant.value.active }
    : null,
  totals: {
    tenants: tenants.value.length,
    activeTenants: tenants.value.filter((t) => t.active).length,
    demoUsers: demoUsers.length,
    demoAudits: demoAudits.length,
  },
    ui: { tab: tab.value },
  }));

async function copyDiagnostics() {
  try {
    await navigator.clipboard.writeText(JSON.stringify(diagnostics.value, null, 2));
    toast("Kopiert");
  } catch {
    toast("Kopieren nicht möglich");
  }
}
</script>
