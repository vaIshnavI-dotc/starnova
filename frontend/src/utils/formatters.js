// Format Indian Rupee values
export function formatINR(val) {
  if (val === null || val === undefined || isNaN(val)) return '—';
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 2,
    minimumFractionDigits: Number.isInteger(val) ? 0 : 2
  }).format(val);
}

// Format percentages with +/- signs
export function formatPct(val, includeSign = true) {
  if (val === null || val === undefined || isNaN(val)) return '—';
  const prefix = includeSign && val > 0 ? '+' : '';
  return `${prefix}${Number(val).toFixed(1)}%`;
}

// Format ISO date string into readable date (e.g. 19 Nov 2026)
export function formatDate(isoStr) {
  if (!isoStr) return '—';
  try {
    const d = new Date(isoStr);
    return d.toLocaleDateString('en-IN', {
      day: 'numeric',
      month: 'short',
      year: 'numeric'
    });
  } catch {
    return isoStr;
  }
}

// Format relative time (e.g. 5m ago, 2h ago, 3d ago)
export function formatRelativeTime(isoStr) {
  if (!isoStr) return '';
  try {
    const d = new Date(isoStr);
    const now = new Date();
    const diffSec = Math.floor((now.getTime() - d.getTime()) / 1000);
    if (diffSec < 60) return 'just now';
    const diffMin = Math.floor(diffSec / 60);
    if (diffMin < 60) return `${diffMin}m ago`;
    const diffHour = Math.floor(diffMin / 60);
    if (diffHour < 24) return `${diffHour}h ago`;
    const diffDay = Math.floor(diffHour / 24);
    if (diffDay < 30) return `${diffDay}d ago`;
    return formatDate(isoStr);
  } catch {
    return '';
  }
}

// Humanize snake_case tags
export function humanizeTag(tag) {
  if (!tag) return '';
  return tag.replace(/_/g, ' ').toUpperCase();
}
