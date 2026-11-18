import type {
  AuthResponse,
  CalculateRequest,
  CalculationResult,
  CarOriginOption,
  CompareRulesResult,
  ExciseKindsResponse,
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

// Backend error texts are English; users see Ukrainian.
const DETAIL_UK: Record<string, string> = {
  'Invalid email or password': 'Невірна електронна пошта або пароль',
  'Email already registered': 'Ця пошта вже зареєстрована. Увійдіть в акаунт',
  'Invalid Google token': 'Не вдалося увійти через Google. Спробуйте ще раз',
  'Not authenticated': 'Сесія завершилася. Увійдіть в акаунт знову',
  'Calculation not found': 'Розрахунок не знайдено (можливо, його вже видалено)',
  'Too many sign-in attempts, try again later':
    'Забагато невдалих спроб входу. Зачекайте 15 хвилин і спробуйте знову',
};

const FIELD_UK: Record<string, string> = {
  item_price: 'Вартість товару',
  shipping_price: 'Вартість доставки',
  car_price: 'Вартість авто',
  quantity: 'Кількість',
  abv: 'Міцність',
  weight_g: 'Вага нетто',
  kind: 'Вид товару',
  engine_volume_cc: "Об'єм двигуна",
  battery_kwh: 'Ємність батареї',
  manufacture_year: 'Рік випуску',
  email: 'Електронна пошта',
  password: 'Пароль',
  password_confirm: 'Повтор пароля',
  name: "Ім'я",
};

// Messages raised by our own backend validators (pydantic prefixes them with "Value error, ").
const VALUE_ERROR_UK: [string, string][] = [
  ['Passwords do not match', 'Паролі не збігаються'],
  ['battery_kwh is required', 'Вкажіть ємність батареї електромобіля'],
  ['engine_volume_cc is required', "Вкажіть об'єм двигуна"],
  ['is a whole number of pieces', 'Кількість штук має бути цілим числом'],
  ['shipped from or through russia is banned', 'Ввезення з рф або транзитом через рф заборонене (постанова КМУ № 426)'],
  ['weight_g is required', 'Вкажіть вагу нетто в грамах'],
  ['abv for', 'Міцність поза допустимими межами для цього напою'],
];

interface ValidationErrorItem {
  loc?: (string | number)[];
  msg?: string;
  type?: string;
  ctx?: Record<string, unknown>;
}

function describeValidationError(err: ValidationErrorItem): string {
  const known = VALUE_ERROR_UK.find(([en]) => err.msg?.includes(en));
  if (known) return known[1];
  const field = [...(err.loc ?? [])].reverse().find((p) => typeof p === 'string' && p in FIELD_UK) as
    | string
    | undefined;
  const ctx = err.ctx ?? {};
  let problem: string;
  switch (err.type) {
    case 'missing':
      problem = "обов'язкове поле";
      break;
    case 'string_too_short':
      problem = `щонайменше ${ctx.min_length} символів`;
      break;
    case 'string_too_long':
      problem = `не більше ${ctx.max_length} символів`;
      break;
    case 'less_than_equal':
      problem = `не більше ${ctx.le}`;
      break;
    case 'greater_than_equal':
      problem = `не менше ${ctx.ge}`;
      break;
    case 'greater_than':
      problem = `має бути більше ${ctx.gt}`;
      break;
    case 'decimal_max_places':
      problem = 'не більше 2 знаків після коми';
      break;
    case 'value_error':
      problem = field === 'email' ? 'некоректна адреса' : 'некоректне значення';
      break;
    default:
      problem = 'некоректне значення';
  }
  return field ? `${FIELD_UK[field]}: ${problem}` : `Перевірте введені дані (${problem})`;
}

function errorMessage(detail: unknown): string | null {
  if (typeof detail === 'string') return DETAIL_UK[detail] ?? detail;
  if (Array.isArray(detail) && detail.length > 0) {
    return [...new Set(detail.map((e: ValidationErrorItem) => describeValidationError(e)))].join('; ');
  }
  return null;
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

  let response: Response;
  try {
    response = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers,
    });
  } catch {
    // Offline, DNS failure, server down: fetch rejects with an English TypeError.
    throw new Error("Немає з'єднання з сервером. Перевірте інтернет і спробуйте ще раз.");
  }

  if (response.status === 401) {
    removeStoredToken();
    window.dispatchEvent(new Event('auth:unauthorized'));
  }

  if (response.status === 204) {
    return {} as T;
  }

  const data = await response.json().catch(() => null);

  if (!response.ok) {
    throw new Error(errorMessage(data?.detail) ?? 'Сталася помилка при зверненні до сервера');
  }

  return data as T;
}

export const api = {
  // Auth
  async signup(email: string, password: string, passwordConfirm: string, name?: string): Promise<AuthResponse> {
    const res = await request<AuthResponse>('/api/auth/signup', {
      method: 'POST',
      body: JSON.stringify({ email, password, password_confirm: passwordConfirm, name: name || undefined }),
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

  async googleAuth(credential: string): Promise<AuthResponse> {
    const res = await request<AuthResponse>('/api/auth/google', {
      method: 'POST',
      body: JSON.stringify({ credential }),
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

  async getCarOrigins(): Promise<CarOriginOption[]> {
    return request<CarOriginOption[]>('/api/car/origins');
  },

  async getExciseKinds(): Promise<ExciseKindsResponse> {
    return request<ExciseKindsResponse>('/api/excise/kinds');
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
