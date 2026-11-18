export type DeliveryType = 'parcel' | 'car';
export type Currency = 'EUR' | 'USD' | 'UAH' | 'GBP' | 'PLN';
export type RulesMode = 'current' | 'july_2027';
export type ParcelSender = 'marketplace' | 'private';

export type EngineType = 'petrol' | 'diesel' | 'hybrid' | 'electric';
export type CarOrigin = 'eu' | 'other';

export interface ParcelCalculateRequest {
  delivery_type: 'parcel';
  item_price: number;
  shipping_price?: number;
  currency?: Currency;
  rules?: RulesMode;
  sender?: ParcelSender;
}

export interface CarCalculateRequest {
  delivery_type: 'car';
  car_price: number;
  shipping_price?: number;
  currency?: Currency;
  engine_type: EngineType;
  engine_volume_cc?: number | null;
  battery_kwh?: number | null;
  manufacture_year: number;
  origin?: CarOrigin;
  // Customs Tariff "new" (never used). Omitted: a car made this year counts as new.
  is_new?: boolean | null;
}

export type CalculateRequest = ParcelCalculateRequest | CarCalculateRequest;

export interface TaxLine {
  code: 'duty' | 'excise' | 'vat';
  label: string;
  amount_eur: string;
  amount_uah: string;
  formula: string;
}

export interface CalculationResult {
  delivery_type: DeliveryType;
  rules: RulesMode;
  input_currency: Currency;
  rate_date: string;
  rate_source: 'nbu' | 'fallback';
  eur_uah: string;
  goods_value_eur: string;
  shipping_eur: string;
  lines: TaxLine[];
  taxes_total_eur: string;
  taxes_total_uah: string;
  landed_total_eur: string;
  landed_total_uah: string;
  notes: string[];
  rates_version: string;
  rates_verified_at: string;
  calculation_id?: number | null;
}

export interface CompareRulesResult {
  current: CalculationResult;
  july_2027: CalculationResult;
}

export interface RatesResponse {
  date: string;
  source: 'nbu' | 'fallback';
  uah_per_unit: Record<string, string>;
}

export interface User {
  id: number;
  email: string;
  name?: string | null;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface HistoryItem {
  id: number;
  created_at: string;
  delivery_type: DeliveryType;
  input: Record<string, unknown>;
  result: CalculationResult;
}

export interface StatsResponse {
  users: number;
  calculations: number;
  calculations_by_signed_in: number;
  returning_users: number;
}
