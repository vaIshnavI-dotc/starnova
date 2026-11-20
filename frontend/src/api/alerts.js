// Alerts API: GET /alerts, POST /alerts/{id}/read, POST /alerts/read_all
import { USE_MOCK, mockDelay, request } from './client';
import { MOCK_ALERTS } from './fixtures';

const ALERTS_STORAGE_KEY = 'sn_mock_alerts_v1';

function getStoredAlerts() {
  try {
    const raw = localStorage.getItem(ALERTS_STORAGE_KEY);
    return raw ? JSON.parse(raw) : [...MOCK_ALERTS];
  } catch {
    return [...MOCK_ALERTS];
  }
}

function saveStoredAlerts(alerts) {
  try {
    localStorage.setItem(ALERTS_STORAGE_KEY, JSON.stringify(alerts));
  } catch {}
}

export async function getAlerts() {
  if (USE_MOCK) {
    await mockDelay(200);
    const alerts = getStoredAlerts();
    const unread_count = alerts.filter(a => !a.read).length;
    return { unread_count, alerts };
  }
  return request('/alerts', { method: 'GET' });
}

export async function markAlertRead(alertId) {
  if (USE_MOCK) {
    await mockDelay(150);
    const alerts = getStoredAlerts();
    const updated = alerts.map(a => a.id === alertId ? { ...a, read: true } : a);
    saveStoredAlerts(updated);
    const unread_count = updated.filter(a => !a.read).length;
    return { unread_count };
  }
  return request(`/alerts/${alertId}/read`, { method: 'POST' });
}

export async function markAllAlertsRead() {
  if (USE_MOCK) {
    await mockDelay(200);
    const alerts = getStoredAlerts();
    const updated = alerts.map(a => ({ ...a, read: true }));
    saveStoredAlerts(updated);
    return { unread_count: 0 };
  }
  return request('/alerts/read_all', { method: 'POST' });
}
