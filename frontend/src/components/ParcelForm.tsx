import React, { useState } from 'react';
import type {
  Currency,
  ParcelCalculateRequest,
  RulesMode,
  ParcelSender,
  CalculationResult,
  CompareRulesResult,
} from '../types/api';
import { api } from '../services/api';
import { parseAmount } from '../utils/amount';
import {
  Package,
  Loader2,
  GitCompare,
  HelpCircle,
  ChevronDown,
  Info,
} from 'lucide-react';

interface ParcelFormProps {
  onCalculated: (result: CalculationResult, request: ParcelCalculateRequest) => void;
  onCompare: (comparison: CompareRulesResult) => void;
  onError: (err: string) => void;
}

const CURRENCY_OPTIONS: { code: Currency; symbol: string; label: string }[] = [
  { code: 'EUR', symbol: '€', label: '€ EUR' },
  { code: 'USD', symbol: '$', label: '$ USD' },
  { code: 'UAH', symbol: '₴', label: '₴ UAH' },
  { code: 'PLN', symbol: 'zł', label: 'zł PLN' },
  { code: 'GBP', symbol: '£', label: '£ GBP' },
];

export const ParcelForm: React.FC<ParcelFormProps> = ({
  onCalculated,
  onCompare,
  onError,
}) => {
  const [itemPrice, setItemPrice] = useState<string>('200');
  const [shippingPrice, setShippingPrice] = useState<string>('15');
  const [currency, setCurrency] = useState<Currency>('EUR');
  const [rules, setRules] = useState<RulesMode>('current');
  const [sender, setSender] = useState<ParcelSender>('marketplace');
  const [showSenderHelp, setShowSenderHelp] = useState(false);
  const [loading, setLoading] = useState(false);
  const [comparing, setComparing] = useState(false);

  // Validates both prices; reports the first problem and returns null if any.
  const readPrices = (): { priceNum: number; shipNum: number } | null => {
    const price = parseAmount(itemPrice, 'вартість товару', { required: true });
    if (price.error !== null) {
      onError(price.error);
      return null;
    }
    const ship = parseAmount(shippingPrice, 'вартість доставки');
    if (ship.error !== null) {
      onError(ship.error);
      return null;
    }
    return { priceNum: price.value, shipNum: ship.value };
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const prices = readPrices();
    if (!prices) return;
    const { priceNum, shipNum } = prices;

    try {
      setLoading(true);
      const req: ParcelCalculateRequest = {
        delivery_type: 'parcel',
        item_price: priceNum,
        shipping_price: shipNum,
        currency,
        rules,
        sender,
      };
      const res = await api.calculate(req);
      onCalculated(res, req);
    } catch (err: unknown) {
      onError(err instanceof Error ? err.message : 'Не вдалося розрахувати');
    } finally {
      setLoading(false);
    }
  };

  const handleCompareClick = async () => {
    const prices = readPrices();
    if (!prices) return;
    const { priceNum, shipNum } = prices;

    try {
      setComparing(true);
      const res = await api.compareRules({
        delivery_type: 'parcel',
        item_price: priceNum,
        shipping_price: shipNum,
        currency,
        sender,
      });
      onCompare(res);
    } catch (err: unknown) {
      onError(err instanceof Error ? err.message : 'Не вдалося порівняти правила');
    } finally {
      setComparing(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Pricing inputs */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {/* Item price */}
        <div>
          <div className="flex items-center justify-between mb-1.5">
            <label htmlFor="parcel-price" className="text-xs font-bold text-slate-700 uppercase tracking-wider">
              1. Вартість товару *
            </label>
            <span className="text-[11px] text-slate-400">інвойсна ціна</span>
          </div>
          <div className="flex rounded-xl shadow-sm border border-slate-300 bg-white overflow-hidden focus-within:ring-2 focus-within:ring-blue-500/30 focus-within:border-blue-500">
            <input
              id="parcel-price"
              type="number"
              step="any"
              min="0"
              required
              value={itemPrice}
              onChange={(e) => setItemPrice(e.target.value)}
              placeholder="200"
              className="flex-1 min-w-0 px-3.5 py-2.5 text-base font-bold text-slate-900 focus:outline-none"
            />
            <div className="relative shrink-0 border-l border-slate-200 bg-slate-100/90 min-w-[100px] lg:min-w-[88px]">
              <select
                value={currency}
                onChange={(e) => setCurrency(e.target.value as Currency)}
                aria-label="Валюта товару"
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
            Будь-які товари рахуються однаково (ст. 374 МКУ). Алкоголь, тютюн і рідини для е-сигарет у посилках фізособам заборонені (ст. 235 МКУ) — див. вкладку «Підакцизні»
          </p>
        </div>

        {/* Shipping price */}
        <div>
          <div className="flex items-center justify-between mb-1.5">
            <label htmlFor="parcel-shipping" className="text-xs font-bold text-slate-700 uppercase tracking-wider">
              2. Вартість доставки
            </label>
            <span className="text-[11px] text-slate-400">до України</span>
          </div>
          <div className="flex rounded-xl shadow-sm border border-slate-300 bg-white overflow-hidden focus-within:ring-2 focus-within:ring-blue-500/30 focus-within:border-blue-500">
            <input
              id="parcel-shipping"
              type="number"
              step="any"
              min="0"
              value={shippingPrice}
              onChange={(e) => setShippingPrice(e.target.value)}
              placeholder="15"
              className="flex-1 min-w-0 px-3.5 py-2.5 text-base font-bold text-slate-900 focus:outline-none"
            />
            <div className="shrink-0 min-w-[88px] bg-slate-100/90 text-slate-900 text-xs font-black px-3 py-2.5 flex items-center justify-center border-l border-slate-200 select-none">
              {CURRENCY_OPTIONS.find((c) => c.code === currency)?.label || currency}
            </div>
          </div>
          <p className="text-[11px] text-slate-500 mt-1">
            Доставка додається до фінальної вартості "під ключ"
          </p>
        </div>
      </div>

      {/* Sender and Rules parameters */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2 border-t border-slate-100">
        {/* Rules mode */}
        <div>
          <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
            За якими правилами рахувати:
          </label>
          <div className="grid grid-cols-2 gap-2">
            <button
              type="button"
              onClick={() => setRules('current')}
              className={`p-2.5 rounded-xl border text-left transition-all ${
                rules === 'current'
                  ? 'border-blue-600 bg-blue-50/70 text-blue-900 font-semibold'
                  : 'border-slate-200 bg-white text-slate-600 hover:border-slate-300'
              }`}
            >
              <div className="text-xs font-bold">Сьогодні</div>
              <div className="text-[11px] text-slate-500">Без мита до €150</div>
            </button>

            <button
              type="button"
              onClick={() => setRules('july_2027')}
              className={`p-2.5 rounded-xl border text-left transition-all ${
                rules === 'july_2027'
                  ? 'border-blue-600 bg-blue-50/70 text-blue-900 font-semibold'
                  : 'border-slate-200 bg-white text-slate-600 hover:border-slate-300'
              }`}
            >
              <div className="text-xs font-bold">Липень 2027</div>
              <div className="text-[11px] text-slate-500">ПДВ 20% від €0</div>
            </button>
          </div>
        </div>

        {/* Sender type */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-1.5">
              <label className="text-xs font-bold text-slate-700 uppercase tracking-wider">
                Хто відправник:
              </label>
              <button
                type="button"
                onClick={() => setShowSenderHelp(!showSenderHelp)}
                aria-label="Чому важливий відправник?"
                title="Натисніть для пояснення"
                className="p-1 rounded-full text-blue-600 hover:text-blue-700 hover:bg-blue-50 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500/30"
              >
                <HelpCircle className="w-4 h-4" />
              </button>
            </div>
            <button
              type="button"
              onClick={() => setShowSenderHelp(!showSenderHelp)}
              className="text-[11px] text-blue-600 hover:underline font-medium py-1.5 px-1 -my-1.5"
            >
              {showSenderHelp ? 'Приховати' : 'Що це означає?'}
            </button>
          </div>

          {showSenderHelp && (
            <div className="mb-3 p-3.5 bg-blue-50 border border-blue-200 rounded-xl text-xs text-blue-950 space-y-1.5 shadow-sm animate-in fade-in">
              <div className="flex items-center justify-between">
                <span className="font-bold flex items-center gap-1.5 text-blue-900">
                  <Info className="w-4 h-4 text-blue-600 shrink-0" />
                  Чому важливий тип відправника?
                </span>
                <button
                  type="button"
                  onClick={() => setShowSenderHelp(false)}
                  className="text-blue-500 hover:text-blue-800 text-xs font-bold px-1"
                >
                  ✕
                </button>
              </div>
              <p className="leading-relaxed text-slate-700">
                За новими законами <strong>№ 5025-IX / 5026-IX</strong> (набувають чинності з <strong>липня 2027</strong>):
              </p>
              <ul className="list-disc list-inside space-y-1 text-slate-700">
                <li>
                  <strong>Онлайн-магазин (маркетплейс):</strong> обов'язковий ПДВ 20% діятиме від €0 на будь-яку комерційну посилку.
                </li>
                <li>
                  <strong>Приватна особа:</strong> подарунки від рідних чи друзів вартістю <strong>до €45 залишаються безмитними</strong>!
                </li>
                <li>
                  <strong>Посилка понад €150:</strong> мито 10% і ПДВ 20% рахуватимуться з <strong>усієї вартості</strong>, а не лише з різниці понад €150.
                </li>
              </ul>
            </div>
          )}

          <div className="grid grid-cols-2 gap-2">
            <button
              type="button"
              onClick={() => setSender('marketplace')}
              className={`p-2.5 rounded-xl border text-left transition-all ${
                sender === 'marketplace'
                  ? 'border-blue-600 bg-blue-50/70 text-blue-900 font-semibold'
                  : 'border-slate-200 bg-white text-slate-600 hover:border-slate-300'
              }`}
            >
              <div className="text-xs font-bold">Онлайн-магазин</div>
              <div className="text-[11px] text-slate-500">Amazon, eBay, etc.</div>
            </button>

            <button
              type="button"
              onClick={() => setSender('private')}
              className={`p-2.5 rounded-xl border text-left transition-all ${
                sender === 'private'
                  ? 'border-blue-600 bg-blue-50/70 text-blue-900 font-semibold'
                  : 'border-slate-200 bg-white text-slate-600 hover:border-slate-300'
              }`}
            >
              <div className="text-xs font-bold">Приватна особа</div>
              <div className="text-[11px] text-slate-500">Подарунок (з 2027: до €45)</div>
            </button>
          </div>
        </div>
      </div>

      {/* Buttons */}
      <div className="flex flex-col sm:flex-row items-center gap-3 pt-2">
        <button
          type="submit"
          disabled={loading || comparing}
          className="w-full sm:flex-1 py-3 px-6 bg-blue-600 hover:bg-blue-700 active:bg-blue-800 text-white font-bold text-sm rounded-xl shadow-md shadow-blue-500/25 transition-all flex items-center justify-center gap-2 disabled:opacity-70"
        >
          {loading ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Розраховуємо...
            </>
          ) : (
            <>
              <Package className="w-4 h-4" />
              Розрахувати розмитнення посилки
            </>
          )}
        </button>

        <button
          type="button"
          onClick={handleCompareClick}
          disabled={loading || comparing}
          className="w-full sm:w-auto py-3 px-5 border border-blue-200 bg-blue-50/60 hover:bg-blue-100/70 text-blue-700 font-semibold text-sm rounded-xl transition-all flex items-center justify-center gap-2 disabled:opacity-70"
        >
          {comparing ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <GitCompare className="w-4 h-4" />
          )}
          Порівняти Зараз vs 2027
        </button>
      </div>
    </form>
  );
};
