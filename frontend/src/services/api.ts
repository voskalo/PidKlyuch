import type {
  AuthResponse,
  CalculateRequest,
  CalculationResult,
  CompareRulesResult,
  HistoryItem,
  ParcelCalculateRequest,
  RatesResponse,
  StatsResponse,
  User,
} from '../types/api';

const API_BASE = import.meta.env.VITE_API_BASE_URL || '';
const TOKEN_KEY = 'pidklyuch_access_token';

export function getStoredToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function setStoredToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
}

export function removeStoredToken(): void {
  localStorage.removeItem(TOKEN_KEY);
}

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const headers = new Headers(options.headers || {});
  
  if (!headers.has('Content-Type') && !(options.body instanceof FormData)) {
    headers.set('Content-Type', 'application/json');
  }

  const token = getStoredToken();
  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  if (response.status === 401) {
    removeStoredToken();
    window.dispatchEvent(new Event('auth:unauthorized'));
  }

  if (response.status === 204) {
    return {} as T;
  }

  const data = await response.json().catch(() => null);

  if (!response.ok) {
    let message = 'Сталася помилка при зверненні до сервера';
    if (data?.detail) {
      if (typeof data.detail === 'string') {
        message = data.detail;
      } else if (Array.isArray(data.detail)) {
        message = data.detail.map((err: { msg?: string }) => err.msg || JSON.stringify(err)).join(', ');
      }
    }
    throw new Error(message);
  }

  return data as T;
}

export const api = {
  // Auth
  async signup(email: string, password: string, name?: string): Promise<AuthResponse> {
    const res = await request<AuthResponse>('/api/auth/signup', {
      method: 'POST',
      body: JSON.stringify({ email, password, name: name || undefined }),
    });
    setStoredToken(res.access_token);
    return res;
  },

  async signin(email: string, password: string): Promise<AuthResponse> {
    const res = await request<AuthResponse>('/api/auth/signin', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    setStoredToken(res.access_token);
    return res;
  },

  async getMe(): Promise<User> {
    return request<User>('/api/auth/me');
  },

  // Calculate
  async calculate(payload: CalculateRequest): Promise<CalculationResult> {
    return request<CalculationResult>('/api/calculate', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  async compareRules(payload: Omit<ParcelCalculateRequest, 'rules'>): Promise<CompareRulesResult> {
    return request<CompareRulesResult>('/api/calculate/compare-rules', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  async getRates(): Promise<RatesResponse> {
    return request<RatesResponse>('/api/rates');
  },

  async getStats(): Promise<StatsResponse> {
    return request<StatsResponse>('/api/stats');
  },

  // History
  async getHistory(): Promise<HistoryItem[]> {
    return request<HistoryItem[]>('/api/history');
  },

  async deleteHistory(id: number): Promise<void> {
    await request<void>(`/api/history/${id}`, {
      method: 'DELETE',
    });
  },
};
