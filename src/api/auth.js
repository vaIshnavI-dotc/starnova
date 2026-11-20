// Auth API: /auth/signup, /auth/login, /auth/me
import { USE_MOCK, mockDelay, request, setToken, removeToken, ApiError } from './client';
import { MOCK_USER } from './fixtures';

export async function signup({ name, email, password }) {
  if (USE_MOCK) {
    await mockDelay(400);
    if (!name || !email || !password) {
      throw new ApiError(422, {
        code: 'validation_error',
        message: 'Name, email, and password are required',
        details: {}
      });
    }
    const token = `sn_mock_token_${Date.now()}`;
    const user = { id: `u_${Date.now()}`, name, email };
    setToken(token);
    return { token, user };
  }

  const res = await request('/auth/signup', {
    method: 'POST',
    body: JSON.stringify({ name, email, password })
  });

  if (res?.token) {
    setToken(res.token);
  }
  return res;
}

export async function login({ email, password }) {
  if (USE_MOCK) {
    await mockDelay(350);
    if (!email || !password) {
      throw new ApiError(422, {
        code: 'validation_error',
        message: 'Email and password are required',
        details: {}
      });
    }
    const token = 'sn_mock_token_demo1234';
    const user = {
      ...MOCK_USER,
      email,
      name: email === 'demo@signalnoise.app' ? MOCK_USER.name : email.split('@')[0]
    };
    setToken(token);
    return { token, user };
  }

  const res = await request('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password })
  });

  if (res?.token) {
    setToken(res.token);
  }
  return res;
}

export async function getMe() {
  if (USE_MOCK) {
    await mockDelay(200);
    return { user: MOCK_USER };
  }
  return request('/auth/me', { method: 'GET' });
}

export function logout() {
  removeToken();
}
