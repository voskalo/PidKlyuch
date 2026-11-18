import React, { useState } from 'react';
import type {
  CarCalculateRequest,
  CalculationResult,
  Currency,
  EngineType,
  CarOrigin,
} from '../types/api';
import { api } from '../services/api';
import { parseAmount } from '../utils/amount';
import {
  Car,
  Fuel,
  Zap,
  Leaf,
  Info,
  Loader2,
  Calendar,
  Layers,
  ChevronDown,
} from 'lucide-react';

interface CarFormProps {
  onCalculated: (result: CalculationResult) => void;
  onError: (err: string) => void;
}

const ENGINE_TYPES: { id: EngineType; label: string; icon: React.ElementType }[] = [
  { id: 'petrol', label: 'Бензин', icon: Fuel },
  { id: 'diesel', label: 'Дизель', icon: Layers },
  { id: 'hybrid', label: 'Гібрид', icon: Leaf },
  { id: 'electric', label: 'Електро', icon: Zap },
];

const CURRENCY_OPTIONS: { code: Currency; symbol: string; label: string }[] = [
  { code: 'EUR', symbol: '€', label: '€ EUR' },
  { code: 'USD', symbol: '$', label: '$ USD' },
  { code: 'UAH', symbol: '₴', label: '₴ UAH' },
  { code: 'PLN', symbol: 'zł', label: 'zł PLN' },
  { code: 'GBP', symbol: '£', label: '£ GBP' },
];

const MIN_YEAR = 1950; // same as the API (manufacture_year ≥ 1950)

// The most common mistake is typing litres ("1.6") instead of cm³ (1600).
function engineVolumeProblem(raw: string): string | null {
  const v = Number(raw);
  if (raw.trim() !== '' && Number.isInteger(v) && v >= 100 && v <= 10000) return null;
  if (v > 0 && v < 20) {
    return `Схоже, це об'єм у літрах. Вкажіть у см³: ${v} л ≈ ${Math.round(v * 1000)} см³`;
  }
  return "Вкажіть об'єм двигуна в см³: ціле число від 100 до 10 000 (наприклад, 1998)";
}

export const CarForm: React.FC<CarFormProps> = ({ onCalculated, onError }) => {
  const [carPrice, setCarPrice] = useState<string>('10000');
  const [shippingPrice, setShippingPrice] = useState<string>('1200');
  const [currency, setCurrency] = useState<Currency>('EUR');
  const [engineType, setEngineType] = useState<EngineType>('petrol');
  const [engineVolumeCc, setEngineVolumeCc] = useState<string>('2000');
  const [batteryKwh, setBatteryKwh] = useState<string>('75');
  const [manufactureYear, setManufactureYear] = useState<string>('2014');
  const [origin, setOrigin] = useState<CarOrigin>('eu');
  // null = the user has not touched the checkbox: then a car made this year counts as new (as in the API)
  const [isNewOverride, setIsNewOverride] = useState<boolean | null>(null);
  const [loading, setLoading] = useState(false);

  const currentYear = new Date().getFullYear();
  const yearNum = parseInt(manufactureYear, 10);
  const kAgeByYear = !isNaN(yearNum)
    ? Math.min(15, Math.max(1, currentYear - yearNum - 1))
    : 1;

  // "New car" (never used) changes the result in two cases, and the checkbox is shown only then:
  //  - 5% duty instead of 10% for non-EU petrol/hybrid cars over 3000 cm³ (Customs Tariff 8703);
  //  - K_age = 1 for any new combustion-engine car, whatever its year (TC 215.3.5-1).
  const newCutsDuty =
    (engineType === 'petrol' || engineType === 'hybrid') && origin === 'other' && Number(engineVolumeCc) > 3000;
  const newCutsKAge = engineType !== 'electric' && kAgeByYear > 1;
  const showIsNew = newCutsDuty || newCutsKAge;
  const isNew = isNewOverride ?? (!isNaN(yearNum) && yearNum >= currentYear);
  const kAge = showIsNew && isNew ? 1 : kAgeByYear;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const price = parseAmount(carPrice, 'вартість авто', { required: true, positive: true });
    if (price.error !== null) {
      onError(price.error);
      return;
    }
    const priceNum = price.value;

    const ship = parseAmount(shippingPrice, 'вартість доставки до кордону');
    if (ship.error !== null) {
      onError(ship.error);
      return;
    }
    const shipNum = ship.value;

    if (!Number.isInteger(Number(manufactureYear)) || yearNum < MIN_YEAR || yearNum > currentYear) {
      onError(`Вкажіть коректний рік випуску авто (від ${MIN_YEAR} до ${currentYear})`);
      return;
    }

    let volumeNum: number | null = null;
    let batteryNum: number | null = null;

    if (engineType === 'electric') {
      batteryNum = Number(batteryKwh);
      if (batteryKwh.trim() === '' || !Number.isFinite(batteryNum) || batteryNum <= 0 || batteryNum > 500) {
        onError('Вкажіть ємність батареї в кВт⋅год: від 1 до 500 (наприклад, 75)');
        return;
      }
    } else {
      const problem = engineVolumeProblem(engineVolumeCc);
      if (problem) {
        onError(problem);
        return;
      }
      volumeNum = Number(engineVolumeCc);
    }

    try {
      setLoading(true);
      const req: CarCalculateRequest = {
        delivery_type: 'car',
        car_price: priceNum,
        shipping_price: shipNum,
        currency,
        engine_type: engineType,
        engine_volume_cc: volumeNum,
        battery_kwh: batteryNum,
        manufacture_year: yearNum,
        origin,
        ...(showIsNew ? { is_new: isNew } : {}),
      };

      const res = await api.calculate(req);
      onCalculated(res);
    } catch (err: unknown) {
      onError(err instanceof Error ? err.message : 'Не вдалося розрахувати розмитнення авто');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* 1. Engine type */}
      <div>
        <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
          1. Тип двигуна
        </label>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
          {ENGINE_TYPES.map((type) => {
            const Icon = type.icon;
            const isSelected = engineType === type.id;
            return (
              <button
                key={type.id}
                type="button"
                onClick={() => setEngineType(type.id)}
                className={`flex items-center justify-center gap-2 p-3 rounded-xl border text-center transition-all ${
                  isSelected
                    ? 'border-blue-600 bg-blue-50/70 text-blue-900 font-semibold shadow-sm'
                    : 'border-slate-200 bg-white hover:border-slate-300 text-slate-600'
                }`}
              >
                <Icon className={`w-4 h-4 ${isSelected ? 'text-blue-600' : 'text-slate-400'}`} />
                <span className="text-xs">{type.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* 2. Prices */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {/* Car price */}
        <div>
          <div className="flex items-center justify-between mb-1.5">
            <label className="text-xs font-bold text-slate-700 uppercase tracking-wider">
              2. Вартість автомобіля *
            </label>
            <span className="text-[11px] text-slate-400">ціна купівлі</span>
          </div>
          <div className="flex rounded-xl shadow-sm border border-slate-300 bg-white overflow-hidden focus-within:ring-2 focus-within:ring-blue-500/30 focus-within:border-blue-500">
            <input
              type="number"
              step="any"
              min="1"
              required
              value={carPrice}
              onChange={(e) => setCarPrice(e.target.value)}
              placeholder="10000"
              className="flex-1 min-w-0 px-3.5 py-2.5 text-base font-bold text-slate-900 focus:outline-none"
            />
            <div className="relative shrink-0 border-l border-slate-200 bg-slate-100/90 min-w-[88px]">
              <select
                value={currency}
                onChange={(e) => setCurrency(e.target.value as Currency)}
                aria-label="Валюта вартості автомобіля"
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
        </div>

        {/* Shipping to border */}
        <div>
          <div className="flex items-center justify-between mb-1.5">
            <label className="text-xs font-bold text-slate-700 uppercase tracking-wider">
              3. Доставка до кордону України
            </label>
            <span className="text-[11px] text-slate-400">входить у митну вартість</span>
          </div>
          <div className="flex rounded-xl shadow-sm border border-slate-300 bg-white overflow-hidden focus-within:ring-2 focus-within:ring-blue-500/30 focus-within:border-blue-500">
            <input
              type="number"
              step="any"
              min="0"
              value={shippingPrice}
              onChange={(e) => setShippingPrice(e.target.value)}
              placeholder="1200"
              className="flex-1 min-w-0 px-3.5 py-2.5 text-base font-bold text-slate-900 focus:outline-none"
            />
            <div className="shrink-0 min-w-[88px] bg-slate-100/90 text-slate-900 text-xs font-black px-3 py-2.5 flex items-center justify-center border-l border-slate-200 select-none">
              {CURRENCY_OPTIONS.find((c) => c.code === currency)?.label || currency}
            </div>
          </div>
        </div>
      </div>

      {/* 3. Engine specs & Year */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {/* Dynamic Engine Volume / Battery capacity */}
        {engineType === 'electric' ? (
          <div>
            <div className="flex items-center justify-between mb-1.5">
              <label className="text-xs font-bold text-slate-700 uppercase tracking-wider">
                4. Ємність батареї (кВт⋅год) *
              </label>
              <span className="text-[11px] text-slate-400">акциз 1 € за 1 кВт⋅год</span>
            </div>
            <div className="flex rounded-xl shadow-sm border border-slate-200 bg-white overflow-hidden focus-within:ring-2 focus-within:ring-blue-500/30 focus-within:border-blue-500">
              <input
                type="number"
                step="any"
                min="1"
                max="500"
                required
                value={batteryKwh}
                onChange={(e) => setBatteryKwh(e.target.value)}
                placeholder="75"
                className="flex-1 min-w-0 px-3.5 py-2.5 text-sm font-semibold text-slate-900 focus:outline-none"
              />
              <div className="shrink-0 min-w-[76px] bg-slate-50 text-slate-600 text-xs font-bold px-2.5 py-2.5 flex items-center justify-center border-l border-slate-200 select-none">
                кВт⋅год
              </div>
            </div>
            <p className="text-[11px] text-slate-500 mt-1">
              Лише для повністю електричних авто: мито 0%, ПДВ 20%. Авто з ДВЗ-генератором (range extender) мають мито 8% і акциз €100 — калькулятор їх не рахує
            </p>
          </div>
        ) : (
          <div>
            <div className="flex items-center justify-between mb-1.5">
              <label className="text-xs font-bold text-slate-700 uppercase tracking-wider">
                4. Об'єм двигуна (см³) *
              </label>
              <span className="text-[11px] text-slate-400">наприклад, 1998</span>
            </div>
            <div className="flex rounded-xl shadow-sm border border-slate-200 bg-white overflow-hidden focus-within:ring-2 focus-within:ring-blue-500/30 focus-within:border-blue-500">
              <input
                type="number"
                min="100"
                max="10000"
                required
                value={engineVolumeCc}
                onInvalid={(e) =>
                  e.currentTarget.setCustomValidity(engineVolumeProblem(e.currentTarget.value) ?? '')
                }
                onChange={(e) => {
                  e.currentTarget.setCustomValidity('');
                  setEngineVolumeCc(e.target.value);
                }}
                placeholder="2000"
                className="flex-1 min-w-0 px-3.5 py-2.5 text-sm font-semibold text-slate-900 focus:outline-none"
              />
              <div className="shrink-0 min-w-[76px] bg-slate-50 text-slate-600 text-xs font-bold px-3 py-2.5 flex items-center justify-center border-l border-slate-200 select-none">
                см³
              </div>
            </div>
            <p className="text-[11px] text-slate-500 mt-1">
              {engineType === 'hybrid'
                ? 'Бензиновий гібрид: акциз за об’ємом ДВЗ за ставкою бензину. Дизельний гібрид — оберіть «Дизель»'
                : 'Впливає на базову ставку та коефіцієнт об’єму'}
            </p>
          </div>
        )}

        {/* Manufacture Year */}
        <div>
          <div className="flex items-center justify-between mb-1.5">
            <label className="text-xs font-bold text-slate-700 uppercase tracking-wider">
              5. Рік випуску *
            </label>
            <span className="text-[11px] text-blue-600 font-semibold flex items-center gap-1">
              <Calendar className="w-3 h-3" />
              Коеф. віку = {kAge}
            </span>
          </div>
          <div className="flex rounded-xl shadow-sm border border-slate-200 bg-white overflow-hidden focus-within:ring-2 focus-within:ring-blue-500/30 focus-within:border-blue-500">
            <input
              type="number"
              min={MIN_YEAR}
              max={currentYear}
              required
              value={manufactureYear}
              onChange={(e) => setManufactureYear(e.target.value)}
              placeholder="2014"
              className="flex-1 min-w-0 px-3.5 py-2.5 text-sm font-semibold text-slate-900 focus:outline-none"
            />
            <div className="shrink-0 min-w-[76px] bg-slate-50 text-slate-600 text-xs font-bold px-3 py-2.5 flex items-center justify-center border-l border-slate-200 select-none">
              рік
            </div>
          </div>
          <p className="text-[11px] text-slate-500 mt-1">
            Згідно з ПКУ: повні роки від наступного року після випуску (макс. 15)
          </p>
        </div>
      </div>

      {/* 4. Origin */}
      <div className="pt-2 border-t border-slate-100">
        <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
          6. Походження авто (сертифікат походження)
        </label>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <button
            type="button"
            onClick={() => setOrigin('eu')}
            className={`p-3 rounded-xl border text-left transition-all ${
              origin === 'eu'
                ? 'border-blue-600 bg-blue-50/70 text-blue-900 font-semibold shadow-sm'
                : 'border-slate-200 bg-white text-slate-600 hover:border-slate-300'
            }`}
          >
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold">Країни ЄС (сертифікат EUR.1)</span>
              <span className="text-[10px] font-bold bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded">
                0% мито
              </span>
            </div>
            <p className="text-[11px] text-slate-500 mt-1">
              Підтверджене походження з Євросоюзу за Угодою про асоціацію
            </p>
          </button>

          <button
            type="button"
            onClick={() => setOrigin('other')}
            className={`p-3 rounded-xl border text-left transition-all ${
              origin === 'other'
                ? 'border-blue-600 bg-blue-50/70 text-blue-900 font-semibold shadow-sm'
                : 'border-slate-200 bg-white text-slate-600 hover:border-slate-300'
            }`}
          >
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold">США, Азія, Канада, інше</span>
              <span className="text-[10px] font-bold bg-blue-100 text-blue-800 px-2 py-0.5 rounded">
                10% мито
              </span>
            </div>
            <p className="text-[11px] text-slate-500 mt-1">
              Стандартна ставка ввізного мита України (5% для нових бензинових авто понад 3000 см³)
            </p>
          </button>
        </div>

        {showIsNew && (
          <label className="mt-3 flex items-start gap-3 p-3 rounded-xl border border-slate-200 bg-white hover:border-slate-300 cursor-pointer transition-all">
            <input
              type="checkbox"
              checked={isNew}
              onChange={(e) => setIsNewOverride(e.target.checked)}
              className="mt-0.5 w-4 h-4 shrink-0 accent-blue-600 cursor-pointer"
            />
            <div>
              <div className="text-xs font-bold text-slate-900">Нове авто (раніше не використовувалося)</div>
              <p className="text-[11px] text-slate-500 mt-0.5">
                {`Для нового авто: ${[
                  newCutsKAge && 'коефіцієнт віку = 1 незалежно від року випуску (ПКУ 215.3.5-1)',
                  newCutsDuty && 'мито 5% замість 10% для бензинових авто й гібридів понад 3000 см³ (Митний тариф, 8703)',
                ]
                  .filter(Boolean)
                  .join('; ')}`}
              </p>
            </div>
          </label>
        )}
      </div>

      <div className="p-3 bg-slate-50 rounded-xl border border-slate-200/80 flex items-start gap-2.5 text-xs text-slate-600">
        <Info className="w-4 h-4 text-blue-500 shrink-0 mt-0.5" />
        <span>
          Розрахунок включає ввізне мито, акцизний податок та 20% ПДВ. Додатково при першій реєстрації в СЦ МВС сплачується збір до ПФ (3–5%) та сертифікація.
        </span>
      </div>

      {/* Submit button */}
      <button
        type="submit"
        disabled={loading}
        className="w-full py-3 px-6 bg-blue-600 hover:bg-blue-700 active:bg-blue-800 text-white font-bold text-sm rounded-xl shadow-md shadow-blue-500/25 transition-all flex items-center justify-center gap-2 disabled:opacity-70"
      >
        {loading ? (
          <>
            <Loader2 className="w-4 h-4 animate-spin" />
            Рахуємо податки на авто...
          </>
        ) : (
          <>
            <Car className="w-4 h-4" />
            Розрахувати розмитнення авто «Під ключ»
          </>
        )}
      </button>
    </form>
  );
};
