/**
 * Format a number as currency (USD)
 */
export function formatCurrency(value: number | null | undefined): string {
  if (value === null || value === undefined || isNaN(value)) {
    return "-";
  }

  // Financial data is typically in millions
  // Format with appropriate scale
  if (Math.abs(value) >= 1000) {
    return `$${(value / 1000).toFixed(1)}B`;
  } else if (Math.abs(value) >= 1) {
    return `$${value.toFixed(1)}M`;
  } else {
    return `$${value.toFixed(2)}`;
  }
}

/**
 * Format a number with thousand separators
 */
export function formatNumber(value: number | null | undefined): string {
  if (value === null || value === undefined || isNaN(value)) {
    return "-";
  }

  return new Intl.NumberFormat("en-US", {
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  }).format(value);
}

/**
 * Format a percentage
 */
export function formatPercent(value: number | null | undefined): string {
  if (value === null || value === undefined || isNaN(value)) {
    return "-";
  }

  return `${(value * 100).toFixed(2)}%`;
}

/**
 * Format bytes to human-readable size
 */
export function formatBytes(bytes: number): string {
  if (bytes === 0) return "0 B";

  const k = 1024;
  const sizes = ["B", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
}
