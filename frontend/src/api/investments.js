// Investments API: POST /investments/confirm, GET /investments, GET /insights
import { USE_MOCK, mockDelay, request, ApiError } from './client';
import { MOCK_INVESTMENTS, MOCK_INSIGHTS } from './fixtures';

const INVESTMENTS_STORAGE_KEY = 'sn_mock_investments_v1';

function getStoredInvestments() {
  try {
    const raw = localStorage.getItem(INVESTMENTS_STORAGE_KEY);
    return raw ? JSON.parse(raw) : [...MOCK_INVESTMENTS];
  } catch {
    return [...MOCK_INVESTMENTS];
  }
}

function saveStoredInvestments(investments) {
  try {
    localStorage.setItem(INVESTMENTS_STORAGE_KEY, JSON.stringify(investments));
  } catch {}
}

export async function confirmInvestment({ confirm_token, ticker, quantity, avg_price, purchase_date }) {
  if (!confirm_token) {
    throw new ApiError(422, {
      code: 'validation_error',
      message: 'confirm_token is required',
      details: {}
    });
  }

  if (USE_MOCK) {
    await mockDelay(350);
    const newInv = {
      id: `inv_${Date.now()}`,
      ticker: ticker || 'TATAMOTORS',
      stock_name: ticker === 'TATAMOTORS' ? 'Tata Motors' : (ticker || 'Confirmed Asset'),
      quantity: Number(quantity) || 10,
      avg_price: Number(avg_price) || 200,
      purchase_date: purchase_date || new Date().toISOString().split('T')[0],
      current_price: 812.4,
      current_value: (Number(quantity) || 10) * 812.4,
      linked_tip_id: 't_9'
    };

    const currentList = getStoredInvestments();
    const updated = [newInv, ...currentList];
    saveStoredInvestments(updated);

    return { investment: newInv };
  }

  const payload = { confirm_token };
  if (ticker !== undefined) payload.ticker = ticker;
  if (quantity !== undefined) payload.quantity = Number(quantity);
  if (avg_price !== undefined) payload.avg_price = Number(avg_price);
  if (purchase_date !== undefined) payload.purchase_date = purchase_date;

  return request('/investments/confirm', {
    method: 'POST',
    body: JSON.stringify(payload)
  });
}

export async function getInvestments() {
  if (USE_MOCK) {
    await mockDelay(250);
    return { investments: getStoredInvestments() };
  }
  return request('/investments', { method: 'GET' });
}

export async function getInsights() {
  if (USE_MOCK) {
    await mockDelay(200);
    return { insights: MOCK_INSIGHTS };
  }
  return request('/insights', { method: 'GET' });
}
