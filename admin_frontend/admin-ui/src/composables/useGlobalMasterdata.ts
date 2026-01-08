import { computed, reactive, readonly } from "vue";
import type { components } from "../api/gen/openapi";

export type GlobalCategory = components["schemas"]["CategoryOut"];
export type GlobalCategoryCreate = components["schemas"]["CategoryCreate"];
export type GlobalCategoryUpdate = components["schemas"]["CategoryUpdate"];

export type GlobalItem = components["schemas"]["ItemOut"];
export type GlobalItemCreate = components["schemas"]["ItemCreate"];
export type GlobalItemUpdate = components["schemas"]["ItemUpdate"];

export type GlobalUnit = components["schemas"]["ItemUnitOut"];

export type GlobalIndustry = {
  id: string;
  name: string;
  description?: string;
  is_active: boolean;
};

export type GlobalType = {
  id: string;
  name: string;
  description?: string;
  is_active: boolean;
};

type IndustryArticleMap = Record<string, string[]>;

const state = reactive({
  categories: [] as GlobalCategory[],
  items: [] as GlobalItem[],
  units: [] as GlobalUnit[],
  industries: [] as GlobalIndustry[],
  types: [] as GlobalType[],
  industryArticles: {} as IndustryArticleMap,
});

function replaceCollection<T>(target: T[], next: T[]) {
  target.splice(0, target.length, ...next);
}

export function generateId() {
  if (typeof crypto !== "undefined" && crypto.randomUUID) {
    return crypto.randomUUID();
  }
  return Math.random().toString(36).slice(2);
}

function upsertCategory(category: GlobalCategory) {
  const idx = state.categories.findIndex((c) => c.id === category.id);
  if (idx >= 0) {
    state.categories.splice(idx, 1, category);
  } else {
    state.categories.push(category);
  }
}

function upsertItem(item: GlobalItem) {
  const idx = state.items.findIndex((c) => c.id === item.id);
  if (idx >= 0) {
    state.items.splice(idx, 1, item);
  } else {
    state.items.push(item);
  }
}

function upsertUnit(entry: GlobalUnit) {
  const idx = state.units.findIndex((c) => c.code === entry.code);
  if (idx >= 0) {
    state.units.splice(idx, 1, entry);
  } else {
    state.units.push(entry);
  }
}

function upsertIndustry(entry: GlobalIndustry) {
  const idx = state.industries.findIndex((c) => c.id === entry.id);
  if (idx >= 0) {
    state.industries.splice(idx, 1, entry);
  } else {
    state.industries.push(entry);
  }
}

function upsertType(entry: GlobalType) {
  const idx = state.types.findIndex((t) => t.id === entry.id);
  if (idx >= 0) {
    state.types.splice(idx, 1, entry);
  } else {
    state.types.push(entry);
  }
}

function setIndustryArticles(industryId: string, articleIds: string[]) {
  state.industryArticles[industryId] = Array.from(new Set(articleIds));
}

function removeIndustry(industryId: string) {
  delete state.industryArticles[industryId];
  const idx = state.industries.findIndex((entry) => entry.id === industryId);
  if (idx >= 0) {
    state.industries.splice(idx, 1);
  }
}

export function useGlobalMasterdata() {
  const categories = computed(() => state.categories);
  const items = computed(() => state.items);
  const units = computed(() => state.units);
  const industries = computed(() => state.industries);
  const types = computed(() => state.types);
  const industryArticles = computed(() => state.industryArticles);

  return {
    categories: readonly(categories),
    items: readonly(items),
    units: readonly(units),
    industries: readonly(industries),
    types: readonly(types),
    industryArticles: readonly(industryArticles),
    upsertCategory,
    upsertItem,
    upsertUnit,
    upsertIndustry,
    upsertType,
    setIndustryArticles,
    removeIndustry,
    replaceCategories(list: GlobalCategory[]) {
      replaceCollection(state.categories, list);
    },
    replaceItems(list: GlobalItem[]) {
      replaceCollection(state.items, list);
    },
    replaceUnits(list: GlobalUnit[]) {
      replaceCollection(state.units, list);
    },
    replaceIndustries(list: GlobalIndustry[]) {
      replaceCollection(state.industries, list);
    },
    replaceTypes(list: GlobalType[]) {
      replaceCollection(state.types, list);
    },
    generateId,
  };
}

export function getCategoryName(categoryId?: string | null) {
  if (!categoryId) return "";
  const match = state.categories.find((c) => c.id === categoryId);
  return match?.name || "";
}
