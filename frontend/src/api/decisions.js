// Decisions API: POST /decisions/lock, GET /decisions
import { USE_MOCK, mockDelay, request, ApiError } from './client';
import { MOCK_DECISIONS } from './fixtures';

const DECISIONS_STORAGE_KEY = 'sn_mock_decisions_v1';

function getStoredDecisions() {
  try {
    const raw = localStorage.getItem(DECISIONS_STORAGE_KEY);
    return raw ? JSON.parse(raw) : [...MOCK_DECISIONS];
  } catch {
    return [...MOCK_DECISIONS];
  }
}

function saveStoredDecisions(decisions) {
  try {
    localStorage.setItem(DECISIONS_STORAGE_KEY, JSON.stringify(decisions));
  } catch {}
}

export async function lockDecision({ decision_id, action, timeframe_days, exit_target, max_loss_pct, confidence }) {
  if (USE_MOCK) {
    await mockDelay(400);

    const missing_fields = [];
    if (!action || !['bought', 'skipped', 'watching'].includes(action)) {
      missing_fields.push('action');
    }
    const days = parseInt(timeframe_days, 10);
    if (!timeframe_days || isNaN(days) || days <= 0) {
      missing_fields.push('timeframe_days');
    }
    const target = parseFloat(exit_target);
    if (!exit_target || isNaN(target) || target <= 0) {
      missing_fields.push('exit_target');
    }
    const loss = parseFloat(max_loss_pct);
    if (!max_loss_pct || isNaN(loss) || loss <= 0 || loss > 100) {
      missing_fields.push('max_loss_pct');
    }
    const conf = parseInt(confidence, 10);
    if (!confidence || isNaN(conf) || conf < 1 || conf > 5) {
      missing_fields.push('confidence');
    }

    if (missing_fields.length > 0) {
      throw new ApiError(422, {
        code: 'gate_incomplete',
        message: 'Please complete all gate requirements before locking',
        details: { missing_fields }
      });
    }

    const lockedAt = new Date().toISOString();
    const newDecision = {
      id: decision_id || `d_${Date.now()}`,
      tip_id: 't_9',
      action,
      timeframe_days: days,
      exit_target: target,
      max_loss_pct: loss,
      confidence: conf,
      thesis: "Thesis challenged across 6 structural links with 3 unverified dependencies.",
      gaps_count: 3,
      locked_at: lockedAt,
      stock: { name: 'Tata Motors', ticker: 'TATAMOTORS' },
      source_name: 'Neel'
    };

    const currentList = getStoredDecisions();
    // Prepend new decision
    const updated = [newDecision, ...currentList.filter(d => d.id !== newDecision.id)];
    saveStoredDecisions(updated);

    return { decision: newDecision };
  }

  return request('/decisions/lock', {
    method: 'POST',
    body: JSON.stringify({
      decision_id,
      action,
      timeframe_days: Number(timeframe_days),
      exit_target: Number(exit_target),
      max_loss_pct: Number(max_loss_pct),
      confidence: Number(confidence)
    })
  });
}

export async function getDecisions() {
  if (USE_MOCK) {
    await mockDelay(300);
    return { decisions: getStoredDecisions() };
  }
  return request('/decisions', { method: 'GET' });
}
