<template>
  <div v-if="open" class="backdrop" @click="$emit('close')"></div>

  <aside v-if="open" class="drawer" @click.stop>
    <div class="drawerHeader">
      <div>
        <div class="drawerTitle">{{ title }}</div>
        <div class="drawerSub mono">{{ row?.id }}</div>
      </div>
      <button class="btnGhost" @click="$emit('close')">Schließen</button>
    </div>

    <div class="drawerBody" v-if="row">
      <div class="kvGrid">
        <div class="kv">
          <div class="k">Zeit</div>
          <div class="v">
            <div class="mono">{{ row.createdAtLocal }}</div>
            <div class="muted mono">{{ row.created_at }}</div>
          </div>
        </div>
        <div class="kv">
          <div class="k">Actor</div>
          <div class="v mono">{{ row.actor }}</div>
        </div>
        <div class="kv">
          <div class="k">Aktion</div>
          <div class="v"><span class="tag neutral">{{ row.actionLabel }}</span></div>
        </div>
        <div class="kv">
          <div class="k">Entity</div>
          <div class="v mono">{{ row.entityLabel }} · {{ row.entity_id }}</div>
        </div>
        <div class="kv">
          <div class="k">Änderung</div>
          <div class="v">{{ row.summary }}</div>
        </div>
      </div>

      <div class="sectionTitle" style="margin-top: 12px;">Payload</div>

      <div class="box">
        <div class="codeHeader">
          <div class="muted">Klick oder Doppelklick kopiert JSON</div>
          <button class="btnGhost" @click="copy">Kopieren</button>
        </div>

        <pre class="code" @dblclick="copy" @click="copy">{{ pretty }}</pre>
      </div>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, watch } from "vue";
import type { AuditDisplayRow } from "./format";
import { actionLabel, entityLabel } from "./format";

const props = defineProps<{
  open: boolean;
  row: AuditDisplayRow | null;
}>();

const emit = defineEmits<{ (e: "close"): void }>();

const pretty = computed(() => {
  if (!props.row) return "";
  return JSON.stringify(props.row.payload ?? {}, null, 2);
});

const title = computed(() => {
  if (!props.row) return "Audit Detail";
  return `${entityLabel(props.row.entity_type)} ${actionLabel(props.row.action)}`;
});

async function copy() {
  try {
    await navigator.clipboard.writeText(pretty.value);
  } catch {
    // bewusst still, Toast liegt im View, nicht im Drawer
  }
}

function handleEsc(e: KeyboardEvent) {
  if (e.key === "Escape") {
    e.stopPropagation();
    emit("close");
  }
}

watch(
  () => props.open,
  (open) => {
    if (open) {
      window.addEventListener("keydown", handleEsc);
    } else {
      window.removeEventListener("keydown", handleEsc);
    }
  },
  { immediate: true }
);

onMounted(() => {
  if (props.open) window.addEventListener("keydown", handleEsc);
});

onUnmounted(() => {
  window.removeEventListener("keydown", handleEsc);
});
</script>
