export type DeliveryType = 'parcel' | 'car' | 'excise';
export type Currency = 'EUR' | 'USD' | 'UAH' | 'GBP' | 'PLN';
export type RulesMode = 'current' | 'july_2027';
export type ParcelSender = 'marketplace' | 'private';

export type EngineType = 'petrol' | 'diesel' | 'hybrid' | 'electric';
// Country of ORIGIN (where the car was made) decides the duty; country of DISPATCH is a separate field.
export type CarOrigin = 'eu' | 'efta' | 'uk' | 'canada' | 'israel' | 'uae' | 'other' | 'unproven';
export type ShippedFrom = 'origin' | 'other' | 'russia';

export interface CarOriginOption {
  key: CarOrigin;
  label: string;
  badge: string;
  hint: string;
}

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
  shipped_from?: ShippedFrom;
  // Customs Tariff "new" (never used). Omitted: a car made this year counts as new.
  is_new?: boolean | null;
}

export type ExciseKindKey =
  | 'beer'
  | 'wine'
  | 'sparkling_wine'
  | 'spirits'
  | 'cigarettes'
  | 'cigars'
  | 'smoking_tobacco'
  | 'heated_tobacco'
  | 'e_liquid'
  | 'petrol'
  | 'diesel';

// Excise goods in one adult's luggage. Not for parcels: MK 235 bans alcohol/tobacco in parcels to private persons.
export interface ExciseCalculateRequest {
  delivery_type: 'excise';
  kind: ExciseKindKey;
  quantity: number; // in the kind's unit (l | ml | pcs | g)
  item_price: number; // for the whole quantity
  currency?: Currency;
  abv?: number | null; // % vol, beer and spirits
  weight_g?: number | null; // net weight, cigars and heated tobacco sticks
  under_24h?: boolean;
}

export interface ExciseKind {
  key: ExciseKindKey;
  label: string;
  group: 'alcohol' | 'tobacco' | 'e_liquid' | 'fuel';
  unit: 'l' | 'ml' | 'pcs' | 'g';
  allowance: string;
  allowance_note: string;
  abv_required: boolean;
  abv_default: string | null;
  abv_min: string | null;
  abv_max: string | null;
  weight_required: boolean;
}

export interface ExciseKindsResponse {
  kinds: ExciseKind[];
  allowance_groups_24h: string[];
  notes: string[];
}

export type CalculateRequest = ParcelCalculateRequest | CarCalculateRequest | ExciseCalculateRequest;

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
