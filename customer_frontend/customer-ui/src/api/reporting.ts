import { api, authHeaders } from "./client";
import type { paths } from "./gen/openapi";
import type { ReportParams, ReportResponse, ReportSeries, ReportKpis } from "@/types/reports";
import { stringifyError } from "@/utils/error";

const DEFAULT_TOP_LIMIT = 5;

type BackendReport = paths["/inventory/report"]["get"]["responses"]["200"]["content"]["application/json"];

function adaptReportParams(params: ReportParams) {
  return {
    ...params,
    item_ids: params.item_ids && params.item_ids.length ? params.item_ids : undefined,
    category_id: params.category_id || undefined,
    aggregate: params.aggregate,
    limit: params.limit ?? DEFAULT_TOP_LIMIT,
  };
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
    throw new Error(stringifyError(error));
  }
}

async function downloadReport(token: string, params: ReportParams, format: "csv" | "excel") {
  const endpoint = `/inventory/reports/export/${format}`;
  const response = await api.get(endpoint, {
    params: adaptReportParams(params),
    responseType: "blob",
    headers: authHeaders(token),
    timeout: 20000,
  });
  return response.data as Blob;
}

export async function exportCsv(token: string, params: ReportParams) {
  return downloadReport(token, params, "csv");
}

export async function exportExcel(token: string, params: ReportParams) {
  return downloadReport(token, params, "excel");
}

function normalizeSeries(series: BackendReport["series"]): ReportSeries[] {
  return (series || []).map((s) => ({
    label: s.label,
    itemId: (s as { itemId?: string }).itemId,
    color: (s as { color?: string }).color,
    data: (s.data || []).map((p) => ({
      ...p,
      item_id: p.item_id || undefined,
      item_name: p.item_name || undefined,
      value: Number(p.value) || 0,
    })),
  }));
}

function normalizeKpis(kpis: BackendReport["kpis"]): ReportKpis {
  const months = kpis?.months || [];
  return {
    totalConsumption: Number(kpis?.totalConsumption ?? 0),
    averagePerMonth: Number(kpis?.averagePerMonth ?? 0),
    months,
    topItem: kpis?.topItem || null,
  };
}
