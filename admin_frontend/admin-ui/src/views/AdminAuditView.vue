<template>
  <div class="grid1">
    <section class="card">
      <header class="cardHeader">
        <div>
          <div class="cardTitle">Audit</div>
          <div class="cardHint">Filter, Pagination, Details</div>
        </div>

        <div class="cardHeaderActions">
          <button class="btnGhost" @click="resetFilters" :disabled="busy.list">Reset</button>
          <button class="btnPrimary" @click="load" :disabled="busy.list">
            {{ busy.list ? "lade..." : "Suchen" }}
          </button>
        </div>
      </header>

      <AuditFiltersBar
        v-model:actor="filters.actor"
        v-model:action="filters.action"
        v-model:entityType="filters.entity_type"
        v-model:entityId="filters.entity_id"
        v-model:createdFrom="filters.created_from"
        v-model:createdTo="filters.created_to"
        v-model:limit="filters.limit"
        :busy="busy.list"
        @enter="load"
      />

      <div class="meta">
        <div class="muted">Einträge: {{ rows.length }}</div>
        <div class="muted">
          Offset: <span class="mono">{{ filters.offset }}</span>
          Limit: <span class="mono">{{ filters.limit }}</span>
        </div>
      </div>

      <AuditTable
        :rows="rows"
        :busy="busy.list"
        @open="openDrawer"
      />

      <div class="rowActions" style="margin-top: 12px;">
        <button class="btnGhost" @click="prevPage" :disabled="busy.list || filters.offset === 0">Prev</button>
        <button class="btnGhost" @click="nextPage" :disabled="busy.list || rows.length < filters.limit">Next</button>

        <div class="muted" style="margin-left: auto;">
          Tipp: Doppelklick auf Payload kopiert JSON im Drawer.
        </div>
      </div>
    </section>

    <AuditDrawer
      :open="drawer.open"
      :row="drawer.row"
      @close="closeDrawer"
    />
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from "vue";
import type { AuditOut } from "../types";
import { adminGetAudit } from "../api/admin";
import { useToast } from "../composables/useToast";

import AuditFiltersBar from "../components/audit/AuditFiltersBar.vue";
import AuditTable from "../components/audit/AuditTable.vue";
import AuditDrawer from "../components/audit/AuditDrawer.vue";

const props = defineProps<{
  adminKey: string;
  actor: string;
}>();

const { toast } = useToast();

const busy = reactive({ list: false });

const filters = reactive({
  actor: "" as string,
  action: "" as string,
  entity_type: "" as string,
  entity_id: "" as string,
  created_from: "" as string, // ISO date-time
  created_to: "" as string,   // ISO date-time
  limit: 100,
  offset: 0,
});

const rows = ref<AuditOut[]>([]);

const drawer = reactive({
  open: false,
  row: null as AuditOut | null,
});

function resetFilters() {
  filters.actor = "";
  filters.action = "";
  filters.entity_type = "";
  filters.entity_id = "";
  filters.created_from = "";
  filters.created_to = "";
  filters.limit = 100;
  filters.offset = 0;
  toast("Filter zurückgesetzt");
}

async function load() {
  if (!props.adminKey) {
    toast("Admin Key fehlt");
    return;
  }

  busy.list = true;
  try {
    const res = await adminGetAudit(props.adminKey, props.actor, {
      actor: filters.actor || undefined,
      action: filters.action || undefined,
      entity_type: filters.entity_type || undefined,
      entity_id: filters.entity_id || undefined,
      created_from: filters.created_from || undefined,
      created_to: filters.created_to || undefined,
      limit: filters.limit,
      offset: filters.offset,
    });

    rows.value = res;
    toast(`Audit geladen: ${res.length}`);
  } catch (e: any) {
    toast(`Fehler: ${stringifyError(e)}`);
  } finally {
    busy.list = false;
  }
}

function nextPage() {
  filters.offset = filters.offset + filters.limit;
  load();
}

function prevPage() {
  filters.offset = Math.max(0, filters.offset - filters.limit);
  load();
}

function openDrawer(row: AuditOut) {
  drawer.open = true;
  drawer.row = row;
}

function closeDrawer() {
  drawer.open = false;
  drawer.row = null;
}

function stringifyError(e: any): string {
  if (!e) return "unknown";
  if (typeof e === "string") return e;
  if (e?.response?.data?.detail) return JSON.stringify(e.response.data.detail);
  if (e?.message) return e.message;
  try { return JSON.stringify(e); } catch { return String(e); }
}

onMounted(() => load());
</script>
