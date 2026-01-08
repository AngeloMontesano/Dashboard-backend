<template>
  <UiPage>
    <UiSection title="Globale Kunden Einstellung" subtitle="Support-Informationen für das Kunden-Frontend">
      <template #actions>
        <button class="btnGhost small" :disabled="state.loading" @click="loadSettings">
          {{ state.loading ? "lädt..." : "Neu laden" }}
        </button>
        <button class="btnPrimary small" :disabled="state.saving || !state.form" @click="saveSettings">
          {{ state.saving ? "speichert..." : "Speichern" }}
        </button>
      </template>

      <div v-if="state.error" class="errorText">Fehler: {{ state.error }}</div>

      <div v-if="state.form" class="stack">
        <div class="table-card">
          <div class="table-card__header">
            <div class="tableTitle">Support Kontakt</div>
            <div class="text-muted text-small">Wird im Hilfe-Overlay angezeigt.</div>
          </div>
          <div class="table-card__body">
            <div class="settings-grid">
              <label class="field">
                <span class="field-label">Telefon</span>
                <input class="input" v-model="state.form.support_phone" :disabled="state.saving" />
              </label>
              <label class="field">
                <span class="field-label">E-Mail</span>
                <input class="input" v-model="state.form.support_email" :disabled="state.saving" />
              </label>
            </div>
          </div>
        </div>

        <details class="table-card" open>
          <summary class="table-card__header">
            <div class="tableTitle">Support Zeiten</div>
            <div class="text-muted text-small">Tage und Uhrzeiten frei als Text pflegen.</div>
          </summary>
          <div class="table-card__body">
            <div class="support-hours">
              <div v-for="(row, index) in state.form.support_hours" :key="index" class="support-hours__row">
                <input
                  class="input"
                  placeholder="Tag (z. B. Mo-Fr)"
                  v-model="row.day"
                  :disabled="state.saving"
                />
                <input
                  class="input"
                  placeholder="Uhrzeit (z. B. 06:00 - 12:00)"
                  v-model="row.time"
                  :disabled="state.saving"
                />
                <button
                  class="btnGhost small danger"
                  type="button"
                  :disabled="state.saving"
                  @click="removeSupportRow(index)"
                >
                  Löschen
                </button>
              </div>
              <button class="btnGhost small" type="button" :disabled="state.saving" @click="addSupportRow">
                + Zeile hinzufügen
              </button>
            </div>
          </div>
        </details>

        <details class="table-card">
          <summary class="table-card__header">
            <div class="tableTitle">Hinweistext</div>
            <div class="text-muted text-small">Für Hinweise wie Schließtage.</div>
          </summary>
          <div class="table-card__body">
            <textarea
              class="input"
              rows="4"
              v-model="state.form.support_note"
              :disabled="state.saving"
              placeholder="z. B. Achtung: am 24.12 geschlossen."
            ></textarea>
          </div>
        </details>
      </div>
    </UiSection>
  </UiPage>
</template>

<script setup lang="ts">
import { onMounted, reactive } from "vue";
import UiPage from "../components/ui/UiPage.vue";
import UiSection from "../components/ui/UiSection.vue";
import { useToast } from "../composables/useToast";
import type { GlobalCustomerSettingsOut, GlobalCustomerSettingsUpdate } from "../types";
import { adminGetGlobalCustomerSettings, adminUpdateGlobalCustomerSettings } from "../api/admin";

const props = defineProps<{
  adminKey: string;
  actor: string;
}>();

const { toast } = useToast();

const state = reactive<{
  loading: boolean;
  saving: boolean;
  error: string;
  form: GlobalCustomerSettingsOut | null;
}>({
  loading: false,
  saving: false,
  error: "",
  form: null,
});

function ensureAdminKey() {
  if (!props.adminKey) {
    state.error = "Kein Admin-Key vorhanden.";
    return false;
  }
  return true;
}

async function loadSettings() {
  if (!ensureAdminKey()) return;
  state.loading = true;
  state.error = "";
  try {
    const res = await adminGetGlobalCustomerSettings(props.adminKey, props.actor);
    state.form = { ...res };
    if (!state.form.support_hours?.length) {
      state.form.support_hours = [{ day: "", time: "" }];
    }
  } catch (error) {
    state.error = (error as Error).message;
    toast(`Globale Einstellungen konnten nicht geladen werden: ${state.error}`, "danger");
  } finally {
    state.loading = false;
  }
}

async function saveSettings() {
  if (!ensureAdminKey() || !state.form) return;
  state.saving = true;
  state.error = "";
  try {
    const payload: GlobalCustomerSettingsUpdate = {
      support_hours: state.form.support_hours,
      support_phone: state.form.support_phone,
      support_email: state.form.support_email,
      support_note: state.form.support_note,
    };
    const res = await adminUpdateGlobalCustomerSettings(props.adminKey, props.actor, payload);
    state.form = { ...res };
    if (!state.form.support_hours?.length) {
      state.form.support_hours = [{ day: "", time: "" }];
    }
    toast("Globale Kunden Einstellungen gespeichert.", "success");
  } catch (error) {
    state.error = (error as Error).message;
    toast(`Speichern fehlgeschlagen: ${state.error}`, "danger");
  } finally {
    state.saving = false;
  }
}

function addSupportRow() {
  if (!state.form) return;
  state.form.support_hours.push({ day: "", time: "" });
}

function removeSupportRow(index: number) {
  if (!state.form) return;
  state.form.support_hours.splice(index, 1);
  if (!state.form.support_hours.length) {
    state.form.support_hours.push({ day: "", time: "" });
  }
}

onMounted(() => {
  loadSettings();
});
</script>

<style scoped>
summary.table-card__header {
  cursor: pointer;
  user-select: none;
}

.support-hours {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.support-hours__row {
  display: grid;
  grid-template-columns: minmax(160px, 1fr) minmax(220px, 1.2fr) auto;
  gap: var(--space-3);
  align-items: center;
}

@media (max-width: 720px) {
  .support-hours__row {
    grid-template-columns: 1fr;
  }
}
</style>
