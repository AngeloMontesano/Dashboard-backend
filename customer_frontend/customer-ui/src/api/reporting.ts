import { api, authHeaders } from "./client";
import type { ReportParams, ReportResponse, ReportSeries, ReportDataPoint, ReportKpis } from "@/types/reports";
import { stringifyError } from "@/utils/error";

const DEFAULT_TOP_LIMIT = 5;

type MovementRecord = {
  id: string;
  type: "IN" | "OUT";
  qty: number | string;
  created_at: string;
  item_id?: string | null;
  item_name?: string | null;
  category_id?: string | null;
  item?: {
    id: string;
    name?: string;
    category_id?: string | null;
  } | null;
};

function adaptReportParams(params: ReportParams) {
  return {
    ...params,
    item_ids: params.item_ids && params.item_ids.length ? params.item_ids : undefined,
    category_id: params.category_id || undefined,
    aggregate: params.aggregate,
    limit: params.limit ?? DEFAULT_TOP_LIMIT,
  };
}

function normalizeSeries(series: ReportSeries[]): ReportSeries[] {
  return (series || []).map((s) => ({
    label: s.label,
    itemId: s.itemId,
    color: s.color,
    data: (s.data || []).map((p) => ({ ...p, value: Number(p.value) || 0 })),
  }));
}

function normalizeKpis(kpis: ReportKpis): ReportKpis {
  const months = kpis?.months || [];
  return {
    totalConsumption: Number(kpis?.totalConsumption ?? 0),
    averagePerMonth: Number(kpis?.averagePerMonth ?? 0),
    months,
    topItem: kpis?.topItem || null,
  };
}

function formatMonthKey(dateValue: string | Date): string {
  const date = typeof dateValue === 'string' ? new Date(dateValue) : dateValue;
  if (Number.isNaN(date.getTime())) return '';
  const month = `${date.getMonth() + 1}`.padStart(2, '0');
  return `${date.getFullYear()}-${month}`;
}

function aggregateMovements(movements: MovementRecord[], params: ReportParams): ReportResponse {
  const monthTotals: Record<string, number> = {};
  const itemMonthTotals: Record<string, { name: string; months: Record<string, number> }> = {};

  const filtered = movements.filter((m) => m.type === 'OUT');

  for (const movement of filtered) {
    if (params.category_id && movement.category_id && movement.category_id !== params.category_id) continue;
    if (params.item_ids && params.item_ids.length && movement.item_id && !params.item_ids.includes(movement.item_id)) {
      continue;
    }

    const period = formatMonthKey(movement.created_at);
    if (!period) continue;

    const qty = Number(movement.qty) || 0;
    monthTotals[period] = (monthTotals[period] || 0) + qty;

    const itemId = movement.item_id || movement.item?.id || 'unknown';
    const itemName = movement.item_name || movement.item?.name || 'Unbekannter Artikel';

    if (!itemMonthTotals[itemId]) {
      itemMonthTotals[itemId] = { name: itemName, months: {} };
    }
    itemMonthTotals[itemId].months[period] = (itemMonthTotals[itemId].months[period] || 0) + qty;
  }

  const months = Object.keys(monthTotals).sort();

  const totalsByItem = Object.entries(itemMonthTotals).map(([itemId, entry]) => {
    const total = Object.values(entry.months).reduce((acc, curr) => acc + curr, 0);
    return { itemId, name: entry.name, total, months: entry.months };
  });

  const topItem = totalsByItem.sort((a, b) => b.total - a.total)[0];

  const aggregateSeries: ReportSeries = {
    label: 'Alle Artikel',
    data: months.map((month) => ({ period: month, value: monthTotals[month] || 0 }))
  };

  const buildItemSeries = (itemId: string, name: string) => {
    const entry = itemMonthTotals[itemId];
    const monthValues = months.map((month) => entry?.months[month] || 0);
    const data: ReportDataPoint[] = months.map((month, index) => ({
      period: month,
      value: monthValues[index],
      item_id: itemId,
      item_name: name,
    }));
    return { label: name, itemId, data } satisfies ReportSeries;
  };

  let series: ReportSeries[] = [];

  if (params.mode === 'top5') {
    const limit = params.limit ?? DEFAULT_TOP_LIMIT;
    const topItems = totalsByItem.sort((a, b) => b.total - a.total).slice(0, limit);
    series = topItems.map((item) => buildItemSeries(item.itemId, item.name));
  } else if (params.mode === 'selected') {
    const requested = params.item_ids || [];
    series = requested.map((itemId) => {
      const entry = itemMonthTotals[itemId];
    const label = entry?.name || 'Artikel';
    return buildItemSeries(itemId, label);
  });
} else {
  if (params.aggregate === false) {
      series = totalsByItem.map((item) => buildItemSeries(item.itemId, item.name));
    } else {
      series = [aggregateSeries];
    }
  }

  const totalConsumption = months.reduce((sum, month) => sum + (monthTotals[month] || 0), 0);
  const averagePerMonth = months.length ? totalConsumption / months.length : 0;

  return {
    series,
    kpis: {
      totalConsumption,
      averagePerMonth,
      months,
      topItem: topItem ? { id: topItem.itemId, name: topItem.name, quantity: topItem.total } : null,
    },
  };
}

async function fetchMovementsForAggregation(token: string, params: ReportParams) {
  const response = await api.get<MovementRecord[] | { items: MovementRecord[] }>("/inventory/movements", {
    params: {
      start: params.from,
      end: params.to,
      category_id: params.category_id || undefined,
      item_ids: params.item_ids && params.item_ids.length ? params.item_ids : undefined,
      type: "OUT",
    },
    headers: authHeaders(token),
    timeout: 20000,
  });
  const data = response.data as any;
  if (Array.isArray(data)) return data;
  if (Array.isArray(data?.items)) return data.items;
  return [];
}

export async function getReportData(token: string, params: ReportParams): Promise<ReportResponse> {
  try {
    const res = await api.get<ReportResponse>("/inventory/report", {
      params: adaptReportParams(params),
      headers: authHeaders(token),
      timeout: 20000,
    });
    return {
      series: normalizeSeries(res.data?.series || []),
      kpis: normalizeKpis(res.data?.kpis),
    };
  } catch (error: any) {
    // TODO Backend: stabilen GET /inventory/report mit o.g. Parametern bereitstellen.
    // Fallback: aggregate clientseitig aus Bewegungen, falls dedizierter Endpoint (noch) fehlt.
    if (error?.response?.status === 404) {
      console.info('[reporting] /inventory/report nicht verfügbar, aggregiere aus Bewegungen');
      const movements = await fetchMovementsForAggregation(token, params);
      return aggregateMovements(movements, params);
    }
    if (error?.response?.status === 405) {
      throw new Error('Reporting-Endpunkt nicht erreichbar (405). Bitte Backend-GET /inventory/report bereitstellen.');
    }
    throw new Error(stringifyError(error));
  }
}

async function downloadReport(token: string, params: ReportParams, format: 'csv' | 'excel') {
  const endpoint = `/inventory/report/export/${format}`;
  const response = await api.get(endpoint, {
    params: adaptReportParams(params),
    responseType: "blob",
    headers: authHeaders(token),
    timeout: 20000,
  });
  return response.data as Blob;
}

export async function exportCsv(token: string, params: ReportParams) {
  return downloadReport(token, params, 'csv');
}

export async function exportExcel(token: string, params: ReportParams) {
  return downloadReport(token, params, 'excel');
}
