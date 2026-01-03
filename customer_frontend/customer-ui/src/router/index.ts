import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router';

import DashboardView from '@/views/DashboardView.vue';
import ArtikelverwaltungView from '@/views/ArtikelverwaltungView.vue';
import LagerbewegungenView from '@/views/LagerbewegungenView.vue';
import InventurView from '@/views/InventurView.vue';
import BerichteAnalysenView from '@/views/BerichteAnalysenView.vue';
import BestellungenView from '@/views/BestellungenView.vue';
import EinstellungenView from '@/views/EinstellungenView.vue';

const routes: RouteRecordRaw[] = [
  { path: '/', name: 'dashboard', component: DashboardView },
  { path: '/artikelverwaltung', name: 'artikelverwaltung', component: ArtikelverwaltungView },
  { path: '/lagerbewegungen', name: 'lagerbewegungen', component: LagerbewegungenView },
  { path: '/inventur', name: 'inventur', component: InventurView },
  { path: '/berichte-analysen', name: 'berichte-analysen', component: BerichteAnalysenView },
  { path: '/bestellungen', name: 'bestellungen', component: BestellungenView },
  { path: '/einstellungen', name: 'einstellungen', component: EinstellungenView }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;
