// Central API Client handling Base URL, Auth headers, 401 redirect, and Mock routing

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

// Default to true unless explicitly set to 'false'
export const USE_MOCK = import.meta.env.VITE_USE_MOCK !== 'false';

const TOKEN_KEY = 'sn_auth_token';
const CONVERSATION_KEY = 'sn_conversation_id';

export function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token) {
  if (token) {
    localStorage.setItem(TOKEN_KEY, token);
  } else {
    localStorage.removeItem(TOKEN_KEY);
  }
}

export function removeToken() {
  localStorage.removeItem(TOKEN_KEY);
}

export function getStoredConversationId() {
  return localStorage.getItem(CONVERSATION_KEY);
}

export function setStoredConversationId(id) {
  if (id) {
    localStorage.setItem(CONVERSATION_KEY, id);
  } else {
    localStorage.removeItem(CONVERSATION_KEY);
  }
}

// Small artificial delay for mock calls
export function mockDelay(ms = 350) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

// Custom API Error conforming to the contract:
// {"error": {"code": "...", "message": "...", "details": {}}}
export class ApiError extends Error {
  constructor(status, errorPayload) {
    super(errorPayload?.message || `API Error ${status}`);
    this.name = 'ApiError';
    this.status = status;
    this.code = errorPayload?.code || 'server_error';
    this.details = errorPayload?.details || {};
    this.error = errorPayload;
  }
}

// Standard fetch wrapper for real endpoints
export async function request(endpoint, options = {}) {
  const token = getToken();
  const headers = { ...options.headers };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  // Do not set Content-Type for FormData (multipart/form-data)
  if (!(options.body instanceof FormData) && !headers['Content-Type']) {
    headers['Content-Type'] = 'application/json';
  }

  const url = `${API_BASE_URL}${endpoint}`;

  let res;
  try {
    res = await fetch(url, {
      ...options,
      headers
    });
  } catch (netErr) {
    throw new ApiError(0, {
      code: 'network_error',
      message: 'Unable to connect to server. Please check your connection.',
      details: { original: netErr.message }
    });
  }

  // Handle 401 Unauthorized globally
  if (res.status === 401) {
    removeToken();
    if (window.location.pathname !== '/login' && window.location.pathname !== '/signup') {
      window.location.href = '/login';
    }
  }

  let data = null;
  const contentType = res.headers.get('content-type');
  if (contentType && contentType.includes('application/json')) {
    try {
      data = await res.json();
    } catch {
      data = null;
    }
  }

  if (!res.ok) {
    const errorPayload = data?.error || {
      code: res.status === 404 ? 'not_found' : 'server_error',
      message: data?.message || `Request failed with status ${res.status}`,
      details: data?.details || {}
    };
    throw new ApiError(res.status, errorPayload);
  }

  return data;
}
