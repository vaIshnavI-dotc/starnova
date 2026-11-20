// Sources API: GET /sources
import { USE_MOCK, mockDelay, request } from './client';
import { MOCK_SOURCES } from './fixtures';

export async function getSources() {
  if (USE_MOCK) {
    await mockDelay(250);
    return { sources: MOCK_SOURCES };
  }
  return request('/sources', { method: 'GET' });
}
