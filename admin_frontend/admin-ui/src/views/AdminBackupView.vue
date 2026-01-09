<template>
  <UiPage>
    <UiSection title="Backup" subtitle="Tenant-spezifische Exporte & Restore (Schema-Introspektion + tenant_id-Pflicht)">
      <BackupContextCard :tenant="tenant" />

      <BackupMonitoringOverview />

      <BackupGuidancePanel />

      <BackupMonitoringDetails />

      <BackupChecksCard />
    </UiSection>
  </UiPage>
</template>

<script setup lang="ts">
import UiPage from "../components/ui/UiPage.vue";
import UiSection from "../components/ui/UiSection.vue";
import BackupContextCard from "../components/backup/BackupContextCard.vue";
import BackupMonitoringOverview from "../components/backup/BackupMonitoringOverview.vue";
import BackupMonitoringDetails from "../components/backup/BackupMonitoringDetails.vue";
import BackupGuidancePanel from "../components/backup/BackupGuidancePanel.vue";
import BackupChecksCard from "../components/backup/BackupChecksCard.vue";

defineProps<{
  tenant: {
    id: string;
    name: string;
    slug: string;
  };
}>();
</script>
