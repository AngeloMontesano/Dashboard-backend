import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router';
import { useAuth } from '@/composables/useAuth';

import DashboardView from '@/views/DashboardView.vue';
import ArtikelverwaltungView from '@/views/ArtikelverwaltungView.vue';
import LagerbewegungenView from '@/views/LagerbewegungenView.vue';
import FehlgeschlageneBuchungenView from '@/views/FehlgeschlageneBuchungenView.vue';
import InventurView from '@/views/InventurView.vue';
import BerichteAnalysenView from '@/views/BerichteAnalysenView.vue';
import BestellungenView from '@/views/BestellungenView.vue';
import EinstellungenView from '@/views/EinstellungenView.vue';
import LoginView from '@/views/LoginView.vue';
import KategorienView from '@/views/KategorienView.vue';

const routes: RouteRecordRaw[] = [
  { path: '/login', name: 'login', component: LoginView, meta: { public: true } },
  { path: '/', name: 'dashboard', component: DashboardView },
  { path: '/artikelverwaltung', name: 'artikelverwaltung', component: ArtikelverwaltungView },
  { path: '/kategorien', name: 'kategorien', component: KategorienView },
  { path: '/lagerbewegungen', name: 'lagerbewegungen', component: LagerbewegungenView },
  { path: '/sync-probleme', name: 'sync-probleme', component: FehlgeschlageneBuchungenView },
  { path: '/inventur', name: 'inventur', component: InventurView },
  { path: '/berichte-analysen', name: 'berichte-analysen', component: BerichteAnalysenView },
  { path: '/bestellungen', name: 'bestellungen', component: BestellungenView },
  { path: '/einstellungen', name: 'einstellungen', component: EinstellungenView }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

router.beforeEach((to) => {
  const { isAuthenticated } = useAuth();
  if (to.meta.public && isAuthenticated()) {
    return { name: 'dashboard' };
  }
  if (to.meta.public) return true;
  if (!isAuthenticated()) {
    return { name: 'login', query: { redirect: to.fullPath } };
  }
  return true;
});

export default router;
