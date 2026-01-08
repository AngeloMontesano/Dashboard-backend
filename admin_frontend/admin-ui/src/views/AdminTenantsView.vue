<template>
  <UiPage>
    <UiSection title="Kunden" subtitle="Kunden suchen und auswählen">
      <template #actions>
        <button class="btnGhost small" @click="openCreateModal">Neuen Kunden anlegen</button>
        <button class="btnGhost small" :disabled="busy.list" @click="loadTenants">
          <span v-if="busy.list" class="spinner" aria-hidden="true"></span>
          {{ busy.list ? "lädt..." : "Neu laden" }}
        </button>
      </template>

      <UiToolbar>
        <template #start>
          <div class="chip-list">
            <UiStatCard label="Kunden gesamt" :value="totalTenants" />
            <UiStatCard label="aktiv" :value="activeTenants" tone="success" />
            <UiStatCard label="deaktiviert" :value="inactiveTenants" tone="danger" />
          </div>
        </template>
        <template #end>
          <div class="toolbar-group">
            <button class="btnGhost small" :disabled="!filteredTenants.length" @click="exportCsv">
              Kunden exportieren CSV
            </button>
            <button class="btnGhost small" :disabled="busy.list" @click="loadTenants">Neu laden</button>
          </div>
        </template>
      </UiToolbar>

      <div class="filter-card two-column">
        <div class="stack">
          <label class="field-label" for="kunden-search">Suche</label>
          <input
            id="kunden-search"
            class="input"
            v-model.trim="q"
            placeholder="Name oder URL-Kürzel eingeben"
            aria-label="Kunden suchen"
          />
          <div class="hint">Tippen zum Filtern. Groß und Kleinschreibung egal. Prefix zuerst, sonst enthält.</div>

          <div class="list-panel">
            <button
              v-for="t in filteredTenants"
              :key="t.id"
              class="list-panel__item"
              :class="{ 'is-active': selectedTenant?.id === t.id }"
              type="button"
              @click="selectTenant(t)"
            >
              <div class="stack-sm">
                <div class="label">{{ t.name }}</div>
                <span class="muted mono">{{ t.slug }}</span>
              </div>
              <span class="badge" :class="t.is_active ? 'tone-success' : 'tone-danger'">
                {{ t.is_active ? "aktiv" : "deaktiviert" }}
              </span>
            </button>
            <div v-if="!filteredTenants.length" class="muted text-small">Keine Kunden gefunden.</div>
          </div>
        </div>

        <div class="stack">
          <label class="field-label" for="kunden-status">Status</label>
          <select id="kunden-status" class="input" v-model="statusFilter" aria-label="Status filtern">
            <option value="all">Alle</option>
            <option value="active">Aktiv</option>
            <option value="disabled">Deaktiviert</option>
          </select>
          <span class="muted text-small">Treffer: {{ filteredTenants.length }}</span>
          <div class="divider"></div>
          <div class="stack">
            <div class="field-label">Ausgewählter Host</div>
            <div class="mono text-small">{{ tenantHost || "—" }}</div>
            <button
              class="btnGhost small"
              type="button"
              :disabled="!selectedTenant"
              @click="resetFilters"
            >
              Filter zurücksetzen
            </button>
          </div>
        </div>
      </div>

      <div class="table-card">
        <div class="table-card__header">
          <div class="tableTitle">Kundenliste</div>
          <div class="text-muted text-small">Zeile anklicken, um auszuwählen.</div>
        </div>
        <div class="table-card__body">
          <div class="tableWrap">
            <table class="table">
              <thead>
                <tr>
                  <th class="narrowCol"></th>
                  <th>Slug</th>
                  <th>Name</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="t in filteredTenants"
                  :key="t.id"
                  :class="{ rowActive: selectedTenant?.id === t.id }"
                  @click="selectTenant(t)"
                >
                  <td class="selectDot">
                    <span class="dot" :class="selectedTenant?.id === t.id ? 'dotActive' : ''"></span>
                  </td>
                  <td class="mono">{{ t.slug }}</td>
                  <td>{{ t.name }}</td>
                  <td>
                    <span class="tag" :class="t.is_active ? 'ok' : 'bad'">
                      {{ t.is_active ? "aktiv" : "deaktiviert" }}
                    </span>
                  </td>
                </tr>
                <tr v-if="!busy.list && filteredTenants.length === 0">
                  <td colspan="4" class="mutedPad">Keine Kunden gefunden.</td>
                </tr>
              </tbody>
            </table>
          </div>
          <div v-if="busy.error" class="errorText">Fehler: {{ busy.error }}</div>
          <div v-if="!busy.list && filteredTenants.length === 0" class="action-row">
            <button class="btnPrimary small" @click="openCreateModal">Ersten Kunden anlegen</button>
            <button class="btnGhost small" @click="resetFilters">Filter zurücksetzen</button>
          </div>
        </div>
      </div>

      <div v-if="selectedTenant" class="detail-card">
        <div class="detail-grid">
          <div class="detail-box">
            <div class="detail-box__label">Name</div>
            <div class="detail-box__value">{{ selectedTenant.name }}</div>
          </div>
          <div class="detail-box">
            <div class="detail-box__label">URL-Kürzel</div>
            <div class="detail-box__value mono">{{ selectedTenant.slug }}</div>
          </div>
          <div class="detail-box detail-box--medium">
            <div class="detail-box__label">Tenant ID</div>
            <div class="detail-box__value mono">{{ selectedTenant.id }}</div>
          </div>
          <div class="detail-box detail-box--wide detail-box--host">
            <div class="detail-box__label">Tenant Host</div>
            <div class="detail-box__value mono detail-box__value--wrap">{{ tenantHost }}</div>
          </div>
        </div>

        <div class="action-row">
          <button
            class="btnGhost small"
            :disabled="busy.toggleId === selectedTenant.id"
            @click="toggleTenant(selectedTenant)"
          >
            {{ busy.toggleId === selectedTenant.id ? "..." : selectedTenant.is_active ? "Deaktivieren" : "Aktivieren" }}
          </button>
          <button
            class="btnGhost small danger"
            :disabled="busy.deleteId === selectedTenant.id"
            @click="deleteTenant(selectedTenant)"
          >
            {{ busy.deleteId === selectedTenant.id ? "löscht..." : "Kunde löschen" }}
          </button>
          <button class="btnPrimary small" @click="openMemberships(selectedTenant.id)">Tenant User verwalten</button>
        </div>

        <div class="divider mt-4"></div>
        <div class="sectionTitle mt-2">Firmendaten & Adresse</div>
        <div v-if="settingsState.error" class="errorText">Fehler: {{ settingsState.error }}</div>
        <div class="settings-grid" v-if="settingsState.form">
          <label class="field">
            <span class="field-label">Firma</span>
            <input class="input" v-model="settingsState.form.company_name" :disabled="settingsState.loading" />
          </label>
          <label class="field">
            <span class="field-label">Ansprechpartner</span>
            <input class="input" v-model="settingsState.form.contact_name" :disabled="settingsState.loading" />
          </label>
          <label class="field">
            <span class="field-label">Kontakt E-Mail</span>
            <input class="input" v-model="settingsState.form.contact_email" :disabled="settingsState.loading" />
          </label>
          <label class="field">
            <span class="field-label">Bestell-E-Mail</span>
            <input class="input" v-model="settingsState.form.order_email" :disabled="settingsState.loading" />
          </label>
          <label class="field">
            <span class="field-label">Telefon</span>
            <input class="input" v-model="settingsState.form.phone" :disabled="settingsState.loading" />
          </label>
          <label class="field">
            <span class="field-label">Straße</span>
            <input class="input" v-model="settingsState.addressStreet" :disabled="settingsState.loading" />
          </label>
          <label class="field">
            <span class="field-label">Hausnummer</span>
            <input class="input" v-model="settingsState.addressNumber" :disabled="settingsState.loading" />
          </label>
          <label class="field">
            <span class="field-label">PLZ</span>
            <input class="input" v-model="settingsState.form.address_postal_code" :disabled="settingsState.loading" />
          </label>
          <label class="field">
            <span class="field-label">Ort</span>
            <input class="input" v-model="settingsState.form.address_city" :disabled="settingsState.loading" />
          </label>
          <label class="field">
            <span class="field-label">Filialnummer</span>
            <input class="input" v-model="settingsState.form.branch_number" :disabled="settingsState.loading" />
          </label>
          <label class="field">
            <span class="field-label">Steuernummer</span>
            <input class="input" v-model="settingsState.form.tax_number" :disabled="settingsState.loading" />
          </label>
          <label class="field">
            <span class="field-label">Kundenbranche</span>
            <select
              class="input"
              v-model="settingsState.form.industry_id"
              :disabled="settingsState.loading"
            >
              <option value="">Keine Auswahl</option>
              <option v-for="branch in industries" :key="branch.id" :value="branch.id">
                {{ branch.name }}
              </option>
            </select>
            <div class="hint">Wird im Tenant-Setting gespeichert und im Customer-Frontend read-only genutzt.</div>
          </label>
          <label class="field">
            <span class="field-label">Export-Format</span>
            <input class="input" v-model="settingsState.form.export_format" :disabled="settingsState.loading" />
          </label>
          <label class="field">
            <span class="field-label">Auto-Bestellung Minimum</span>
            <input
              class="input"
              type="number"
              min="0"
              v-model.number="settingsState.form.auto_order_min"
              :disabled="settingsState.loading"
            />
          </label>
          <label class="field checkbox">
            <input type="checkbox" v-model="settingsState.form.auto_order_enabled" :disabled="settingsState.loading" />
            <span>Auto-Bestellung aktiv</span>
          </label>
        </div>
        <div class="action-row" v-if="settingsState.form">
          <button class="btnGhost small" type="button" :disabled="settingsState.loading" @click="loadTenantSettings(selectedTenant.id)">
            Neu laden
          </button>
          <button class="btnPrimary small" type="button" :disabled="settingsState.saving" @click="saveTenantSettings">
            {{ settingsState.saving ? "speichert..." : "Speichern" }}
          </button>
        </div>
      </div>

      <TenantCreateModal
        :open="modal.open"
        :busy="busy.create"
        :baseDomain="baseDomain"
        v-model:name="modal.name"
        v-model:slug="modal.slug"
        @close="closeCreateModal"
        @create="createTenant"
      />
    </UiSection>
  </UiPage>
</template>

<script setup lang="ts">
/*
  Kunden-Ansicht
  - Live-Suche (Prefix-first), case insensitive
  - Tabelle nur zur Auswahl
  - Detailbereich mit Aktionen
  - CSV-Export aus gefilterter Liste
*/
import { computed, reactive, ref, watch } from "vue";
import type { TenantOut, TenantSettingsOut, TenantSettingsUpdate } from "../types";
import {
  adminListTenants,
  adminCreateTenant,
  adminUpdateTenant,
  adminDeleteTenant,
  adminGetTenantSettings,
  adminUpdateTenantSettings,
  adminListIndustries,
} from "../api/admin";
import { useToast } from "../composables/useToast";
import { useGlobalMasterdata } from "../composables/useGlobalMasterdata";

import TenantCreateModal from "../components/tenants/TenantCreateModal.vue";
import UiPage from "../components/ui/UiPage.vue";
import UiSection from "../components/ui/UiSection.vue";
import UiToolbar from "../components/ui/UiToolbar.vue";
import UiStatCard from "../components/ui/UiStatCard.vue";

const props = defineProps<{
  adminKey: string;
  actor: string;
  apiOk: boolean;
  dbOk: boolean;
  selectedTenantId?: string;
}>();

const emit = defineEmits<{
  (e: "openMemberships", tenantId: string): void;
  (e: "tenantSelected", payload: { id: string; name: string; slug: string } | null): void;
}>();

const { toast } = useToast();
const { industries, replaceIndustries } = useGlobalMasterdata();

/* State */
const tenants = ref<TenantOut[]>([]);
const selectedTenant = ref<TenantOut | null>(null);

const q = ref("");
const statusFilter = ref<"all" | "active" | "disabled">("all");

const totalTenants = computed(() => tenants.value.length);
const activeTenants = computed(() => tenants.value.filter((t) => t.is_active).length);
const inactiveTenants = computed(() => tenants.value.filter((t) => !t.is_active).length);

const busy = reactive({
  list: false,
  create: false,
  toggleId: "" as string,
  deleteId: "" as string,
  error: "",
});

const settingsState = reactive<{
  loading: boolean;
  saving: boolean;
  error: string;
  form: TenantSettingsUpdate | null;
  addressStreet: string;
  addressNumber: string;
}>({
  loading: false,
  saving: false,
  error: "",
  form: null,
  addressStreet: "",
  addressNumber: "",
});

/* Modal State */
const modal = reactive({
  open: false,
  name: "",
  slug: "",
});

const baseDomain = import.meta.env.VITE_BASE_DOMAIN || "test.myitnetwork.de";
const tenantHost = computed(() => (selectedTenant.value ? `${selectedTenant.value.slug}.${baseDomain}` : ""));

/* Filter */
const filteredTenants = computed(() => {
  let list = tenants.value.slice();
  if (statusFilter.value === "active") list = list.filter((t) => t.is_active);
  if (statusFilter.value === "disabled") list = list.filter((t) => !t.is_active);

  const term = q.value.trim().toLowerCase();
  if (!term) return list;

  const prefix = list.filter(
    (t) => t.slug.toLowerCase().startsWith(term) || t.name.toLowerCase().startsWith(term)
  );
  if (prefix.length) return prefix;
  return list.filter((t) => t.slug.toLowerCase().includes(term) || t.name.toLowerCase().includes(term));
});

/* API: Load Tenants */
async function loadTenants() {
  if (!ensureAdminKey()) return;
  busy.list = true;
  busy.error = "";
  try {
    const res = await adminListTenants(props.adminKey, props.actor, {
      limit: 500,
      offset: 0,
    });
    tenants.value = res;
    // Default: keine Auswahl
    if (selectedTenant.value) {
      selectedTenant.value = res.find((t) => t.id === selectedTenant.value.id) ?? null;
    }
    emitSelectedTenant();
    toast(`Kunden geladen: ${res.length}`);
  } catch (e: any) {
    busy.error = stringifyError(e);
    toast(`Fehler beim Laden: ${busy.error}`);
  } finally {
    busy.list = false;
  }
}

/* API: Create Tenant */
async function createTenant() {
  if (!ensureAdminKey()) return;
  const name = modal.name.trim();
  const slug = modal.slug.trim().toLowerCase();

  if (!name || !slug) {
    toast("Name und URL-Kürzel sind Pflicht");
    return;
  }

  if (!/^[a-z0-9-]+$/.test(slug)) {
    toast("URL-Kürzel: nur Kleinbuchstaben, Zahlen und Bindestriche erlaubt");
    return;
  }

  busy.create = true;
  try {
    const created = await adminCreateTenant(props.adminKey, props.actor, { name, slug });
    tenants.value = [created, ...tenants.value];
    selectedTenant.value = created;
    closeCreateModal();
    toast("Kunde angelegt");
  } catch (e: any) {
    toast(`Fehler beim Anlegen: ${stringifyError(e)}`);
  } finally {
    busy.create = false;
  }
}

/* API: Toggle Tenant Active */
async function toggleTenant(t: TenantOut) {
  if (!ensureAdminKey()) return;
  if (!t) return;

  const actionLabel = t.is_active ? "deaktivieren" : "aktivieren";
  const ok = window.confirm(`Kunde ${t.slug} wirklich ${actionLabel}?`);
  if (!ok) return;

  busy.toggleId = t.id;
  try {
    const updated = await adminUpdateTenant(props.adminKey, props.actor, t.id, {
      is_active: !t.is_active,
    });
    tenants.value = tenants.value.map((x) => (x.id === updated.id ? updated : x));
    if (selectedTenant.value?.id === updated.id) selectedTenant.value = updated;
    toast(updated.is_active ? "Kunde aktiviert" : "Kunde deaktiviert");
  } catch (e: any) {
    toast(`Fehler beim Update: ${stringifyError(e)}`);
  } finally {
    busy.toggleId = "";
  }
}

async function deleteTenant(t: TenantOut) {
  if (!ensureAdminKey()) return;
  if (!t) return;
  const confirmed = window.confirm(`Kunde ${t.slug} wirklich löschen? Diese Aktion ist irreversibel.`);
  if (!confirmed) return;
  const check = window.prompt(
    `Bitte Tenant ID zur Bestätigung eingeben:\n${t.id}\nLöschen kann nicht rückgängig gemacht werden.`
  );
  if (!check || check.trim() !== t.id) {
    toast("Löschen abgebrochen: Tenant ID stimmt nicht.");
    return;
  }

  busy.deleteId = t.id;
  try {
    await adminDeleteTenant(props.adminKey, props.actor, t.id);
    tenants.value = tenants.value.filter((x) => x.id !== t.id);
    if (selectedTenant.value?.id === t.id) selectedTenant.value = null;
    toast("Kunde gelöscht");
  } catch (e: any) {
    toast(`Fehler beim Löschen: ${stringifyError(e)}`);
  } finally {
    busy.deleteId = "";
  }
}

/* UI actions */
function selectTenant(t: TenantOut) {
  selectedTenant.value = t;
  emitSelectedTenant();
  if (t?.id) {
    loadTenantSettings(t.id);
  } else {
    settingsState.form = null;
  }
}

function openCreateModal() {
  modal.open = true;
  modal.name = "";
  modal.slug = "";
}

function closeCreateModal() {
  modal.open = false;
}

function openMemberships(tenantId: string) {
  emit("openMemberships", tenantId);
}

function resetFilters() {
  q.value = "";
  statusFilter.value = "all";
}

async function loadIndustriesList() {
  if (!ensureAdminKey()) return;
  try {
    const res = await adminListIndustries(props.adminKey, props.actor);
    replaceIndustries(res as any);
  } catch (e: any) {
    toast(`Branchen konnten nicht geladen werden: ${stringifyError(e)}`);
  }
}

async function loadTenantSettings(tenantId: string) {
  if (!ensureAdminKey()) return;
  settingsState.loading = true;
  settingsState.error = "";
  try {
    const res = await adminGetTenantSettings(props.adminKey, props.actor, tenantId);
    settingsState.form = { ...(res as TenantSettingsOut) };
    const split = splitAddress(settingsState.form.address || "");
    settingsState.addressStreet = split.street;
    settingsState.addressNumber = split.number;
  } catch (e: any) {
    settingsState.error = stringifyError(e);
    toast(`Einstellungen konnten nicht geladen werden: ${settingsState.error}`);
  } finally {
    settingsState.loading = false;
  }
}

async function saveTenantSettings() {
  if (!ensureAdminKey() || !selectedTenant.value || !settingsState.form) return;
  settingsState.saving = true;
  settingsState.error = "";
  try {
    settingsState.form.address = composeAddress(settingsState.addressStreet, settingsState.addressNumber);
    const payload = { ...settingsState.form } as TenantSettingsUpdate;
    const updated = await adminUpdateTenantSettings(props.adminKey, props.actor, selectedTenant.value.id, payload);
    settingsState.form = { ...(updated as TenantSettingsOut) };
    const split = splitAddress(settingsState.form.address || "");
    settingsState.addressStreet = split.street;
    settingsState.addressNumber = split.number;
    toast("Einstellungen gespeichert");
  } catch (e: any) {
    settingsState.error = stringifyError(e);
    toast(`Speichern fehlgeschlagen: ${settingsState.error}`);
  } finally {
    settingsState.saving = false;
  }
}

async function copyValue(value: string, label: string) {
  try {
    await navigator.clipboard.writeText(value);
    toast(`${label} kopiert`);
  } catch {
    toast(`${label} konnte nicht kopiert werden`);
  }
}

function ensureAdminKey(): boolean {
  if (!props.adminKey) {
    toast("Bitte Admin Key setzen");
    return false;
  }
  return true;
}

function emitSelectedTenant() {
  if (selectedTenant.value) {
    emit("tenantSelected", {
      id: selectedTenant.value.id,
      name: selectedTenant.value.name,
      slug: selectedTenant.value.slug,
    });
  } else {
    emit("tenantSelected", null);
  }
}

function stringifyError(e: any): string {
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

function exportCsv() {
  if (!filteredTenants.value.length) {
    toast("Keine Kunden zum Export");
    return;
  }
  const header = ["slug", "name", "status", "tenant_id", "host"];
  const rows = filteredTenants.value.map((t) => [
    t.slug,
    t.name,
    t.is_active ? "aktiv" : "deaktiviert",
    t.id,
    `${t.slug}.${baseDomain}`,
  ]);
  const csv = [
    header.join(";"),
    ...rows.map((r) => r.map((cell) => `"${String(cell).replace(/"/g, '""')}"`).join(";")),
  ].join("\n");
  const stamp = new Date();
  const pad = (n: number) => String(n).padStart(2, "0");
  const filename = `kunden_export_${stamp.getFullYear()}${pad(stamp.getMonth() + 1)}${pad(stamp.getDate())}_${pad(
    stamp.getHours()
  )}${pad(stamp.getMinutes())}.csv`;
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
  toast("Export erstellt");
}

watch(
  () => props.adminKey,
  (key, prev) => {
    if (key && key !== prev) {
      loadTenants();
      loadIndustriesList();
    }
  },
  { immediate: true }
);

function splitAddress(address: string) {
  const match = address?.match(/^(.*?)(\s+\d+\w*)$/);
  return {
    street: match ? match[1].trim() : (address || "").trim(),
    number: match ? match[2].trim() : "",
  };
}

function composeAddress(street: string, number: string) {
  return [street?.trim(), number?.trim()].filter(Boolean).join(" ");
}
</script>
