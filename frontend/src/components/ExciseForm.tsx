import React, { useEffect, useState } from 'react';
import type {
  CalculationResult,
  Currency,
  ExciseCalculateRequest,
  ExciseKind,
  ExciseKindKey,
  ExciseKindsResponse,
} from '../types/api';
import { api } from '../services/api';
import { parseAmount } from '../utils/amount';
import { KIND_UI } from '../constants/excise';
import {
  Loader2,
  ChevronDown,
  ShieldAlert,
  Luggage,
  Info,
} from 'lucide-react';

interface ExciseFormProps {
  onCalculated: (result: CalculationResult, request: ExciseCalculateRequest) => void;
  onError: (err: string) => void;
}

const GROUPS: { id: ExciseKind['group'][]; label: string }[] = [
  { id: ['alcohol'], label: 'Алкоголь' },
  { id: ['tobacco'], label: 'Тютюн' },
  { id: ['e_liquid', 'fuel'], label: 'Рідини та пальне' },
];

const UNIT_LABEL: Record<ExciseKind['unit'], string> = { l: 'л', ml: 'мл', pcs: 'шт', g: 'г' };

const CURRENCY_OPTIONS: { code: Currency; label: string }[] = [
  { code: 'EUR', label: '€ EUR' },
  { code: 'USD', label: '$ USD' },
  { code: 'UAH', label: '₴ UAH' },
  { code: 'PLN', label: 'zł PLN' },
  { code: 'GBP', label: '£ GBP' },
];

const fmt = (value: string | null) => (value === null ? '' : String(Number(value)));

export const ExciseForm: React.FC<ExciseFormProps> = ({ onCalculated, onError }) => {
  const [catalog, setCatalog] = useState<ExciseKindsResponse | null>(null);
  const [catalogError, setCatalogError] = useState<string | null>(null);
  const [kindKey, setKindKey] = useState<ExciseKindKey>('spirits');
  const [quantity, setQuantity] = useState(KIND_UI.spirits.quantity);
  const [price, setPrice] = useState(KIND_UI.spirits.price);
  const [currency, setCurrency] = useState<Currency>('EUR');
  const [abv, setAbv] = useState('40');
  const [weight, setWeight] = useState('');
  const [under24h, setUnder24h] = useState(false);
  const [loading, setLoading] = useState(false);

  const fetchCatalog = () =>
    api
      .getExciseKinds()
      .then(setCatalog)
      .catch((err: unknown) =>
        setCatalogError(err instanceof Error ? err.message : 'Не вдалося завантажити перелік товарів'),
      );

  useEffect(() => {
    fetchCatalog();
  }, []);

  const retryCatalog = () => {
    setCatalogError(null);
    fetchCatalog();
  };

  const kind = catalog?.kinds.find((k) => k.key === kindKey) ?? null;
  const unit = kind ? UNIT_LABEL[kind.unit] : '';
  const has24hRule = !!kind && !!catalog?.allowance_groups_24h.includes(kind.group);

  const selectKind = (k: ExciseKind) => {
    setKindKey(k.key);
    setQuantity(KIND_UI[k.key].quantity);
    setPrice(KIND_UI[k.key].price);
    setAbv(fmt(k.abv_default));
    setWeight('');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!kind) return;

    const qty = Number(quantity.trim().replace(',', '.'));
    if (quantity.trim() === '' || !Number.isFinite(qty) || qty <= 0 || qty > 100000) {
      onError(`Вкажіть кількість (${unit}): більше 0 і не більше 100 000`);
      return;
    }
    if (kind.unit === 'pcs' && !Number.isInteger(qty)) {
      onError('Кількість штук має бути цілим числом');
      return;
    }

    let abvNum: number | null = null;
    if (kind.abv_required) {
      abvNum = Number(abv.trim().replace(',', '.'));
      const min = Number(kind.abv_min);
      const max = Number(kind.abv_max);
      if (abv.trim() === '' || !Number.isFinite(abvNum) || abvNum < min || abvNum > max) {
        onError(`Міцність для «${KIND_UI[kind.key].short}»: від ${min}% до ${max}%`);
        return;
      }
      abvNum = Math.round(abvNum * 10) / 10;
    }

    let weightNum: number | null = null;
    if (kind.weight_required) {
      weightNum = Number(weight.trim().replace(',', '.'));
      if (weight.trim() === '' || !Number.isFinite(weightNum) || weightNum <= 0 || weightNum > 100000) {
        onError('Вкажіть вагу нетто всієї кількості в грамах (вказана на пачці / коробці)');
        return;
      }
      weightNum = Math.round(weightNum * 10) / 10;
    }

    const parsedPrice = parseAmount(price, 'ціну покупки', { required: true });
    if (parsedPrice.error !== null) {
      onError(parsedPrice.error);
      return;
    }

    const req: ExciseCalculateRequest = {
      delivery_type: 'excise',
      kind: kind.key,
      quantity: Math.round(qty * 1000) / 1000,
      item_price: parsedPrice.value,
      currency,
      abv: abvNum,
      weight_g: weightNum,
      under_24h: has24hRule && under24h,
    };
    try {
      setLoading(true);
      onCalculated(await api.calculate(req), req);
    } catch (err: unknown) {
      onError(err instanceof Error ? err.message : 'Не вдалося розрахувати податки');
    } finally {
      setLoading(false);
    }
  };

  if (catalogError) {
    return (
      <div className="p-4 rounded-xl bg-red-50 border border-red-200 text-sm text-red-700 space-y-2">
        <p>{catalogError}</p>
        <button
          type="button"
          onClick={retryCatalog}
          className="px-3 py-1.5 bg-red-600 hover:bg-red-700 text-white rounded-lg text-xs font-semibold"
        >
          Спробувати знову
        </button>
      </div>
    );
  }

  if (!catalog || !kind) {
    return (
      <div className="py-10 flex items-center justify-center gap-2 text-sm text-slate-500">
        <Loader2 className="w-4 h-4 animate-spin text-blue-600" />
        Завантажуємо перелік товарів...
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Postal ban (MK 235): the most important fact for this tab */}
      <div className="flex items-start gap-2.5 p-3 rounded-xl bg-amber-50 border border-amber-200 text-xs text-amber-900">
        <ShieldAlert className="w-4 h-4 shrink-0 mt-0.5 text-amber-600" />
        <span className="leading-relaxed">
          <strong>Лише для ввезення в багажі.</strong> Алкоголь, тютюн і рідини для е-сигарет на адресу фізосіб
          поштою та кур'єром пересилати заборонено (ст. 235 МКУ), пальне не приймають як небезпечний вантаж.
        </span>
      </div>

      {/* 1. Kind */}
      <div className="space-y-3">
        <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider">1. Що ввозите</label>
        {GROUPS.map((group) => (
          <div key={group.label}>
            <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1.5">{group.label}</div>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
              {catalog.kinds
                .filter((k) => group.id.includes(k.group))
                .map((k) => {
                  const Icon = KIND_UI[k.key].icon;
                  const selected = k.key === kindKey;
                  return (
                    <button
                      key={k.key}
                      type="button"
                      onClick={() => selectKind(k)}
                      aria-pressed={selected}
                      className={`flex flex-col items-center justify-center gap-1.5 p-3 min-h-[68px] rounded-xl border text-center transition-all ${
                        selected
                          ? 'border-blue-600 bg-blue-50/70 text-blue-900 font-semibold shadow-sm'
                          : 'border-slate-200 bg-white hover:border-slate-300 text-slate-600'
                      }`}
                    >
                      <Icon className={`w-4 h-4 shrink-0 ${selected ? 'text-blue-600' : 'text-slate-400'}`} />
                      <span className="text-xs leading-tight">{KIND_UI[k.key].short}</span>
                    </button>
                  );
                })}
            </div>
          </div>
        ))}
      </div>

      {/* 2. Quantity (+ strength / weight) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <div className="flex items-center justify-between gap-2 mb-1.5">
            <label className="text-xs font-bold text-slate-700 uppercase tracking-wider">2. Кількість *</label>
            <span className="text-[11px] text-slate-400 text-right">{kind.label}</span>
          </div>
          <div className="flex rounded-xl shadow-sm border border-slate-300 bg-white overflow-hidden focus-within:ring-2 focus-within:ring-blue-500/30 focus-within:border-blue-500">
            <input
              type="number"
              inputMode="decimal"
              step={kind.unit === 'pcs' ? 1 : 'any'}
              min={kind.unit === 'pcs' ? 1 : 0}
              max={100000}
              required
              value={quantity}
              onChange={(e) => setQuantity(e.target.value)}
              aria-label={`Кількість, ${unit}`}
              className="flex-1 min-w-0 px-3.5 py-2.5 text-base font-bold text-slate-900 focus:outline-none"
            />
            <div className="shrink-0 min-w-[76px] bg-slate-50 text-slate-600 text-xs font-bold px-3 py-2.5 flex items-center justify-center border-l border-slate-200 select-none">
              {unit}
            </div>
          </div>
          <p className="text-[11px] text-slate-500 mt-1">
            Безмитно на 1 особу від 18 років: <strong className="text-slate-700">{kind.allowance_note}</strong>
          </p>
        </div>

        {kind.abv_required && (
          <div>
            <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">Міцність *</label>
            <div className="flex rounded-xl shadow-sm border border-slate-300 bg-white overflow-hidden focus-within:ring-2 focus-within:ring-blue-500/30 focus-within:border-blue-500">
              <input
                type="number"
                inputMode="decimal"
                step="0.1"
                min={fmt(kind.abv_min)}
                max={fmt(kind.abv_max)}
                required
                value={abv}
                onChange={(e) => setAbv(e.target.value)}
                aria-label="Міцність, % об."
                className="flex-1 min-w-0 px-3.5 py-2.5 text-base font-bold text-slate-900 focus:outline-none"
              />
              <div className="shrink-0 min-w-[76px] bg-slate-50 text-slate-600 text-xs font-bold px-3 py-2.5 flex items-center justify-center border-l border-slate-200 select-none">
                % об.
              </div>
            </div>
            <p className="text-[11px] text-slate-500 mt-1">
              Акциз рахується від чистого спирту ({fmt(kind.abv_min)}–{fmt(kind.abv_max)}%)
            </p>
          </div>
        )}

        {kind.weight_required && (
          <div>
            <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
              Вага нетто *
            </label>
            <div className="flex rounded-xl shadow-sm border border-slate-300 bg-white overflow-hidden focus-within:ring-2 focus-within:ring-blue-500/30 focus-within:border-blue-500">
              <input
                type="number"
                inputMode="decimal"
                step="any"
                min="0"
                max={100000}
                required
                value={weight}
                onChange={(e) => setWeight(e.target.value)}
                placeholder={kind.key === 'cigars' ? '600' : '300'}
                aria-label="Вага нетто, г"
                className="flex-1 min-w-0 px-3.5 py-2.5 text-base font-bold text-slate-900 focus:outline-none"
              />
              <div className="shrink-0 min-w-[76px] bg-slate-50 text-slate-600 text-xs font-bold px-3 py-2.5 flex items-center justify-center border-l border-slate-200 select-none">
                г
              </div>
            </div>
            <p className="text-[11px] text-slate-500 mt-1">Усієї кількості, без упаковки (вказана на коробці)</p>
          </div>
        )}
      </div>

      {/* 3. Price */}
      <div>
        <div className="flex items-center justify-between gap-2 mb-1.5">
          <label className="text-xs font-bold text-slate-700 uppercase tracking-wider">3. Ціна покупки *</label>
          <span className="text-[11px] text-slate-400">за всю кількість</span>
        </div>
        <div className="flex rounded-xl shadow-sm border border-slate-300 bg-white overflow-hidden focus-within:ring-2 focus-within:ring-blue-500/30 focus-within:border-blue-500">
          <input
            type="number"
            inputMode="decimal"
            step="any"
            min="0"
            required
            value={price}
            onChange={(e) => setPrice(e.target.value)}
            aria-label="Ціна покупки"
            className="flex-1 min-w-0 px-3.5 py-2.5 text-base font-bold text-slate-900 focus:outline-none"
          />
          <div className="relative shrink-0 border-l border-slate-200 bg-slate-100/90 min-w-[100px] lg:min-w-[88px]">
            <select
              value={currency}
              onChange={(e) => setCurrency(e.target.value as Currency)}
              aria-label="Валюта ціни"
              className="w-full h-full appearance-none bg-transparent pl-3 pr-7 py-2.5 text-xs font-black text-slate-900 focus:outline-none cursor-pointer hover:bg-slate-200/70 transition-colors"
            >
              {CURRENCY_OPTIONS.map((c) => (
                <option key={c.code} value={c.code}>
                  {c.label}
                </option>
              ))}
            </select>
            <ChevronDown className="w-4 h-4 text-slate-600 absolute right-2 top-1/2 -translate-y-1/2 pointer-events-none" />
          </div>
        </div>
        <p className="text-[11px] text-slate-500 mt-1">
          Податки — лише з кількості понад норму, пропорційно до ціни
          {kind.key === 'cigarettes' ? '; адвалорна частина акцизу (12%) — від ціни покупки' : ''}
        </p>
      </div>

      {has24hRule && (
        <label className="flex items-start gap-3 p-3 rounded-xl border border-slate-200 bg-white hover:border-slate-300 cursor-pointer transition-all">
          <input
            type="checkbox"
            checked={under24h}
            onChange={(e) => setUnder24h(e.target.checked)}
            className="mt-0.5 w-4 h-4 shrink-0 accent-blue-600 cursor-pointer"
          />
          <div>
            <div className="text-xs font-bold text-slate-900">Я був(ла) за кордоном менше 24 годин</div>
            <p className="text-[11px] text-slate-500 mt-0.5">
              Тоді безмитна норма на алкоголь і тютюн не діє (ст. 376 ч. 3 МКУ)
            </p>
          </div>
        </label>
      )}

      <div className="p-3 bg-slate-50 rounded-xl border border-slate-200/80 flex items-start gap-2.5 text-xs text-slate-600">
        <Info className="w-4 h-4 text-blue-500 shrink-0 mt-0.5" />
        <span>
          Понад безмитну норму сплачуються мито, акциз і ПДВ 20% — без порогу €150/€500, як для звичайних товарів (ст. 234
          ч. 6, ст. 376 МКУ). Розрахунок на одну особу; кожен вид товару рахуйте окремо.
        </span>
      </div>

      <button
        type="submit"
        disabled={loading}
        className="w-full py-3 px-6 bg-blue-600 hover:bg-blue-700 active:bg-blue-800 text-white font-bold text-sm rounded-xl shadow-md shadow-blue-500/25 transition-all flex items-center justify-center gap-2 disabled:opacity-70"
      >
        {loading ? (
          <>
            <Loader2 className="w-4 h-4 animate-spin" />
            Рахуємо...
          </>
        ) : (
          <>
            <Luggage className="w-4 h-4" />
            Розрахувати податки на підакцизні товари
          </>
        )}
      </button>
    </form>
  );
};
