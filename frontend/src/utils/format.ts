import dayjs from 'dayjs';

export function formatDate(value: string | null | undefined, fmt = 'YYYY-MM-DD'): string {
  if (!value) return '-';
  return dayjs(value).format(fmt);
}

export function formatDateTime(value: string | null | undefined): string {
  return formatDate(value, 'YYYY-MM-DD HH:mm:ss');
}

export function formatCurrency(value: number | null | undefined, currency?: string): string {
  if (value == null) return '-';
  const formatted = Number(value).toLocaleString('zh-CN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
  return currency ? `${formatted} ${currency}` : formatted;
}

export function formatDecimal(value: number | null | undefined, digits = 2): string {
  if (value == null) return '-';
  return Number(value).toFixed(digits);
}

export function formatEnum(
  value: string | null | undefined,
  labelMap: Record<string, string>,
): string {
  if (!value) return '-';
  return labelMap[value] || value;
}
