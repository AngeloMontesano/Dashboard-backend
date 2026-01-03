<template>
  <div v-if="open" class="backdrop" @click="$emit('close')"></div>

  <aside v-if="open" class="drawer" @click.stop>
    <div class="drawerHeader">
      <div>
        <div class="drawerTitle">Audit Detail</div>
        <div class="drawerSub mono">{{ row?.id }}</div>
      </div>
      <button class="btnGhost" @click="$emit('close')">Schließen</button>
    </div>

    <div class="drawerBody" v-if="row">
      <div class="kvGrid">
        <div class="kv">
          <div class="k">Zeit</div>
          <div class="v mono">{{ row.created_at }}</div>
        </div>
        <div class="kv">
          <div class="k">Actor</div>
          <div class="v mono">{{ row.actor }}</div>
        </div>
        <div class="kv">
          <div class="k">Action</div>
          <div class="v"><span class="tag neutral">{{ row.action }}</span></div>
        </div>
        <div class="kv">
          <div class="k">Entity</div>
          <div class="v mono">{{ row.entity_type }} · {{ row.entity_id }}</div>
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
import { computed } from "vue";
import type { AuditOut } from "../../types";

const props = defineProps<{
  open: boolean;
  row: AuditOut | null;
}>();

defineEmits<{ (e: "close"): void }>();

const pretty = computed(() => {
  if (!props.row) return "";
  return JSON.stringify(props.row.payload ?? {}, null, 2);
});

async function copy() {
  try {
    await navigator.clipboard.writeText(pretty.value);
  } catch {
    // bewusst still, Toast liegt im View, nicht im Drawer
  }
}
</script>
