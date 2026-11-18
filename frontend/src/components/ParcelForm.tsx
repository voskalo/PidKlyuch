import React, { useState } from 'react';
import type {
  Currency,
  ParcelCategory,
  ParcelCalculateRequest,
  RulesMode,
  ParcelSender,
  CalculationResult,
  CompareRulesResult,
} from '../types/api';
import { api } from '../services/api';
import {
  Package,
  Laptop,
  Shirt,
  Sparkles,
  Gamepad2,
  Box,
  Loader2,
  GitCompare,
  HelpCircle,
  ChevronDown,
} from 'lucide-react';

interface ParcelFormProps {
  onCalculated: (result: CalculationResult) => void;
  onCompare: (comparison: CompareRulesResult) => void;
  onError: (err: string) => void;
}

const CATEGORIES: { id: ParcelCategory; label: string; icon: React.ElementType }[] = [
  { id: 'electronics', label: 'Електроніка', icon: Laptop },
  { id: 'clothing', label: 'Одяг та взуття', icon: Shirt },
  { id: 'cosmetics', label: 'Косметика', icon: Sparkles },
  { id: 'toys', label: 'Іграшки', icon: Gamepad2 },
  { id: 'other', label: 'Інше', icon: Box },
];

const CURRENCIES: Currency[] = ['EUR', 'USD', 'UAH', 'PLN', 'GBP'];

export const ParcelForm: React.FC<ParcelFormProps> = ({
  onCalculated,
  onCompare,
  onError,
}) => {
  const [category, setCategory] = useState<ParcelCategory>('electronics');
  const [itemPrice, setItemPrice] = useState<string>('200');
  const [shippingPrice, setShippingPrice] = useState<string>('15');
  const [currency, setCurrency] = useState<Currency>('EUR');
  const [rules, setRules] = useState<RulesMode>('current');
  const [sender, setSender] = useState<ParcelSender>('marketplace');
  const [loading, setLoading] = useState(false);
  const [comparing, setComparing] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const priceNum = parseFloat(itemPrice);
    if (isNaN(priceNum) || priceNum < 0) {
      onError('Вкажіть коректну вартість товару');
      return;
    }

    const shipNum = shippingPrice ? parseFloat(shippingPrice) : 0;
    if (isNaN(shipNum) || shipNum < 0) {
      onError('Вкажіть коректну вартість доставки');
      return;
    }

    try {
      setLoading(true);
      const req: ParcelCalculateRequest = {
        delivery_type: 'parcel',
        category,
        item_price: priceNum,
        shipping_price: shipNum,
        currency,
        rules,
        sender,
      };
      const res = await api.calculate(req);
      onCalculated(res);
    } catch (err: unknown) {
      onError(err instanceof Error ? err.message : 'Не вдалося розрахувати');
    } finally {
      setLoading(false);
    }
  };

  const handleCompareClick = async () => {
    const priceNum = parseFloat(itemPrice);
    if (isNaN(priceNum) || priceNum < 0) {
      onError('Вкажіть коректну вартість товару для порівняння');
      return;
    }

    const shipNum = shippingPrice ? parseFloat(shippingPrice) : 0;

    try {
      setComparing(true);
      const res = await api.compareRules({
        delivery_type: 'parcel',
        category,
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
      {/* Category selector */}
      <div>
        <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
          1. Категорія товару
        </label>
        <div className="grid grid-cols-2 sm:grid-cols-5 gap-2">
          {CATEGORIES.map((cat) => {
            const Icon = cat.icon;
            const isSelected = category === cat.id;
            return (
              <button
                key={cat.id}
                type="button"
                onClick={() => setCategory(cat.id)}
                className={`flex flex-col items-center justify-center p-3 rounded-xl border text-center transition-all ${
                  isSelected
                    ? 'border-blue-600 bg-blue-50/70 text-blue-900 font-semibold shadow-sm'
                    : 'border-slate-200 bg-white hover:border-slate-300 text-slate-600'
                }`}
              >
                <Icon className={`w-5 h-5 mb-1.5 ${isSelected ? 'text-blue-600' : 'text-slate-400'}`} />
                <span className="text-xs">{cat.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Pricing inputs */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {/* Item price */}
        <div>
          <div className="flex items-center justify-between mb-1.5">
            <label className="text-xs font-bold text-slate-700 uppercase tracking-wider">
              2. Вартість товару *
            </label>
            <span className="text-[11px] text-slate-400">інвойсна ціна</span>
          </div>
          <div className="flex rounded-xl shadow-sm border border-slate-200 bg-white overflow-hidden focus-within:ring-2 focus-within:ring-blue-500/30 focus-within:border-blue-500">
            <input
              type="number"
              step="any"
              min="0"
              required
              value={itemPrice}
              onChange={(e) => setItemPrice(e.target.value)}
              placeholder="200"
              className="flex-1 min-w-0 px-3.5 py-2.5 text-sm font-semibold text-slate-900 focus:outline-none"
            />
            <div className="relative shrink-0 border-l border-slate-200 bg-slate-50 min-w-[76px]">
              <select
                value={currency}
                onChange={(e) => setCurrency(e.target.value as Currency)}
                aria-label="Валюта товару"
                className="w-full h-full appearance-none bg-transparent pl-3 pr-7 py-2.5 text-xs font-bold text-slate-700 focus:outline-none cursor-pointer hover:bg-slate-100 transition-colors"
              >
                {CURRENCIES.map((c) => (
                  <option key={c} value={c}>
                    {c}
                  </option>
                ))}
              </select>
              <ChevronDown className="w-3.5 h-3.5 text-slate-400 absolute right-2 top-1/2 -translate-y-1/2 pointer-events-none" />
            </div>
          </div>
          <p className="text-[11px] text-slate-500 mt-1">
            Для посилок мито розраховується від фактурної вартості товарів
          </p>
        </div>

        {/* Shipping price */}
        <div>
          <div className="flex items-center justify-between mb-1.5">
            <label className="text-xs font-bold text-slate-700 uppercase tracking-wider">
              3. Вартість доставки
            </label>
            <span className="text-[11px] text-slate-400">до України</span>
          </div>
          <div className="flex rounded-xl shadow-sm border border-slate-200 bg-white overflow-hidden focus-within:ring-2 focus-within:ring-blue-500/30 focus-within:border-blue-500">
            <input
              type="number"
              step="any"
              min="0"
              value={shippingPrice}
              onChange={(e) => setShippingPrice(e.target.value)}
              placeholder="15"
              className="flex-1 min-w-0 px-3.5 py-2.5 text-sm font-semibold text-slate-900 focus:outline-none"
            />
            <div className="shrink-0 min-w-[76px] bg-slate-50 text-slate-600 text-xs font-bold px-3 py-2.5 flex items-center justify-center border-l border-slate-200 select-none">
              {currency}
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
          <div className="flex items-center gap-1.5 mb-2">
            <label className="text-xs font-bold text-slate-700 uppercase tracking-wider">
              Хто відправник:
            </label>
            <div className="group relative cursor-pointer" title="Для правил липня 2027 приватні подарунки до €45 безмитні">
              <HelpCircle className="w-3.5 h-3.5 text-slate-400" />
            </div>
          </div>
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
              <div className="text-[11px] text-slate-500">Подарунок від рідних</div>
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
