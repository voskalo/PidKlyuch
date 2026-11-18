// Parsing of money typed by the user. Mirrors the API limits (backend/app/api/schemas_calc.py: Amount):
// 0 ≤ amount ≤ 10 000 000, at most 2 decimal places.

export const MAX_AMOUNT = 10_000_000;

export type ParsedAmount = { value: number; error: null } | { value: null; error: string };

/**
 * `what` is the field name in Ukrainian (feminine, e.g. "вартість товару").
 * Empty input is 0 unless `required`. Extra decimals are rounded to cents (19.999 → 20.00).
 */
export function parseAmount(
  raw: string,
  what: string,
  opts: { required?: boolean; positive?: boolean } = {},
): ParsedAmount {
  const text = raw.trim().replace(',', '.');
  const What = what.charAt(0).toUpperCase() + what.slice(1);
  if (text === '') {
    return opts.required ? { value: null, error: `Вкажіть ${what}` } : { value: 0, error: null };
  }
  const value = Number(text);
  if (!Number.isFinite(value)) {
    return { value: null, error: `${What}: введіть число, наприклад 199.99` };
  }
  if (value < 0) {
    return { value: null, error: `${What} не може бути від'ємною` };
  }
  if (opts.positive && value === 0) {
    return { value: null, error: `${What} має бути більшою за 0` };
  }
  if (value > MAX_AMOUNT) {
    return { value: null, error: `${What} не може перевищувати 10 000 000` };
  }
  return { value: Math.round(value * 100) / 100, error: null };
}
