export type ReportMode = 'top5' | 'all' | 'selected';

export type ReportParams = {
  start: string;
  end: string;
  mode: ReportMode;
  item_ids?: string[];
  category_id?: string;
  aggregate?: boolean;
  limit?: number;
};

export type ReportDataPoint = {
  period: string; // YYYY-MM
  value: number;
  item_id?: string;
  item_name?: string;
};

export type ReportSeries = {
  label: string;
  itemId?: string;
  color?: string;
  data: ReportDataPoint[];
};

export type ReportTopItem = {
  id: string;
  name: string;
  quantity: number;
};

export type ReportKpis = {
  totalConsumption: number;
  averagePerMonth: number;
  months: string[];
  topItem?: ReportTopItem | null;
};

export type ReportResponse = {
  series: ReportSeries[];
  kpis: ReportKpis;
};

export type CategoryOption = {
  label: string;
  value: string;
};

export type ItemOption = {
  label: string;
  value: string;
  categoryId?: string | null;
};

export type ReportFilterState = {
  dateRange: [Date | null, Date | null];
  appliedRange: [Date | null, Date | null];
  mode: ReportMode;
  categoryId: string | null;
  selectedItems: ItemOption[];
  aggregateAll: boolean;
  topLimit: number;
};
