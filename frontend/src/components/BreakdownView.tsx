import React from 'react';
import type { CalculationResult } from '../types/api';
import {
  ShieldCheck,
  Calendar,
  AlertTriangle,
  Info,
  CheckCircle,
  Bookmark,
  LogIn,
} from 'lucide-react';

interface BreakdownViewProps {
  result: CalculationResult;
  onOpenAuth?: () => void;
  onCompareRules?: () => void;
}

export const BreakdownView: React.FC<BreakdownViewProps> = ({
  result,
  onOpenAuth,
  onCompareRules,
}) => {
  const isZeroTax = result.lines.length === 0;

  return (
    <div className="space-y-5 animate-in fade-in duration-300">
      {/* Top Total Card */}
      <div className="bg-gradient-to-br from-slate-900 via-slate-800 to-blue-950 text-white rounded-2xl p-6 shadow-xl border border-slate-700/60 relative overflow-hidden">
        <div className="absolute top-0 right-0 w-64 h-64 bg-blue-500/10 rounded-full blur-3xl pointer-events-none" />
        
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div>
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-blue-500/20 text-blue-300 border border-blue-400/20 mb-2">
              <ShieldCheck className="w-3.5 h-3.5 text-blue-400" />
              Разом «Під ключ» (Landed Cost)
            </div>
            <div className="flex items-baseline gap-3 flex-wrap">
              <span className="text-3xl sm:text-4xl font-extrabold tracking-tight text-white">
                {result.landed_total_uah} ₴
              </span>
              <span className="text-lg sm:text-xl font-medium text-slate-300">
                ({result.landed_total_eur} €)
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-1">
              Повна вартість: ціна товару + доставка + усі податки
            </p>
          </div>

          <div className="bg-white/10 backdrop-blur-md rounded-xl p-4 border border-white/10 md:min-w-[220px]">
            <div className="text-xs text-slate-300 font-medium">Сума податків:</div>
            <div className="text-2xl font-bold text-amber-300 mt-0.5">
              {result.taxes_total_uah} ₴
            </div>
            <div className="text-xs text-slate-400">
              ({result.taxes_total_eur} €)
            </div>

            <div className="mt-2 pt-2 border-t border-white/10 text-[11px] text-slate-300 flex justify-between">
              <span>Товар + доставка:</span>
              <span>{(parseFloat(result.goods_value_eur) + parseFloat(result.shipping_eur)).toFixed(2)} €</span>
            </div>
          </div>
        </div>
      </div>

      {/* Tax free banner if 0 taxes */}
      {isZeroTax && (
        <div className="bg-emerald-50 border border-emerald-200 rounded-2xl p-5 flex items-start gap-3.5 text-emerald-900">
          <CheckCircle className="w-6 h-6 text-emerald-600 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <h4 className="font-bold text-sm">
              Безмитне ввезення — податки 0 грн!
            </h4>
            <p className="text-xs text-emerald-700 leading-relaxed">
              {result.delivery_type === 'excise'
                ? 'Кількість у межах безмитної норми на одну особу (ст. 376 МКУ) — мито, акциз і ПДВ не сплачуються.'
                : result.rules === 'july_2027'
                ? 'Ця посилка є подарунком від фізичної особи вартістю до €45, тому відповідно до нових правил не підлягає оподаткуванню.'
                : 'Вартість товарів не перевищує митний ліміт €150 (ст. 374 МКУ). Мито та ПДВ не нараховуються.'}
            </p>
          </div>
        </div>
      )}

      {/* Itemized lines breakdown */}
      {!isZeroTax && (
        <div className="bg-white rounded-2xl border border-slate-200/90 shadow-sm overflow-hidden">
          <div className="p-4 bg-slate-50 border-b border-slate-200/80 flex items-center justify-between">
            <h4 className="font-bold text-slate-800 text-sm flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-blue-600" />
              Деталізація митних платежів
            </h4>
            <span className="text-xs text-slate-500">
              {result.lines.length} {result.lines.length === 1 ? 'платіж' : 'платежі'}
            </span>
          </div>

          <div className="divide-y divide-slate-100">
            {result.lines.map((line) => (
              <div key={line.code} className="p-4 sm:p-5 space-y-2 hover:bg-slate-50/50 transition-colors">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className={`text-[11px] font-bold px-2 py-0.5 rounded uppercase tracking-wider ${
                      line.code === 'duty'
                        ? 'bg-blue-100 text-blue-800'
                        : line.code === 'excise'
                        ? 'bg-purple-100 text-purple-800'
                        : 'bg-amber-100 text-amber-800'
                    }`}>
                      {line.code}
                    </span>
                    <span className="font-semibold text-slate-900 text-sm sm:text-base">
                      {line.label}
                    </span>
                  </div>

                  <div className="text-right">
                    <span className="font-bold text-slate-900 text-sm sm:text-base">
                      {line.amount_uah} ₴
                    </span>
                    <span className="text-xs text-slate-500 ml-1.5">
                      ({line.amount_eur} €)
                    </span>
                  </div>
                </div>

                {/* Mathematical formula container */}
                <div className="bg-slate-100/80 rounded-xl px-3 py-2 border border-slate-200/60 font-mono text-xs text-slate-700 flex items-center justify-between flex-wrap gap-2">
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] uppercase font-sans font-bold text-slate-400 bg-white px-1.5 py-0.5 rounded border border-slate-200">
                      Формула
                    </span>
                    <span className="break-all">{line.formula}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Compare button for parcels */}
      {result.delivery_type === 'parcel' && onCompareRules && (
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200/80 rounded-2xl p-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
          <div className="space-y-0.5">
            <h5 className="font-bold text-blue-950 text-sm">
              Цікаво, скільки це коштуватиме після липня 2027?
            </h5>
            <p className="text-xs text-blue-700">
              Порівняйте поточний розрахунок із майбутніми правилами обов’язкового ПДВ від €0.
            </p>
          </div>
          <button
            onClick={onCompareRules}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs rounded-xl shadow-sm transition-colors shrink-0"
          >
            Порівняти правила
          </button>
        </div>
      )}

      {/* Notes & legal verification status */}
      <div className="bg-slate-50 border border-slate-200 rounded-2xl p-4 space-y-3 text-xs text-slate-600">
        <div className="flex flex-wrap items-center justify-between gap-2 pb-2 border-b border-slate-200">
          <div className="flex items-center gap-1.5 text-slate-700 font-medium">
            <Calendar className="w-3.5 h-3.5 text-blue-600" />
            <span>Ставки перевірено за законодавством:</span>
            <span className="font-semibold text-slate-900 bg-white px-2 py-0.5 rounded border border-slate-200">
              {result.rates_verified_at}
            </span>
          </div>

          <div className="flex items-center gap-1.5 text-slate-500">
            <span>Курс НБУ (1 € = {parseFloat(result.eur_uah).toFixed(2)} ₴)</span>
            {result.rate_source === 'fallback' && (
              <span className="text-amber-600 font-semibold">(резервний)</span>
            )}
          </div>
        </div>

        {result.notes && result.notes.length > 0 && (
          <div className="space-y-1.5">
            {result.notes.map((note, idx) => (
              <div key={idx} className="flex items-start gap-2 text-slate-600">
                <Info className="w-3.5 h-3.5 text-blue-500 shrink-0 mt-0.5" />
                <span className="leading-relaxed">{note}</span>
              </div>
            ))}
          </div>
        )}

        {result.rate_source === 'fallback' && (
          <div className="flex items-start gap-2 text-amber-700 bg-amber-50 p-2.5 rounded-xl border border-amber-200">
            <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5 text-amber-600" />
            <span>
              Увага: сервер НБУ був тимчасово недоступний, тому використано фіксований курс валют. Підсумкова сума в гривні може незначно відрізнятися.
            </span>
          </div>
        )}

        {/* History indicator */}
        <div className="pt-2 border-t border-slate-200 flex items-center justify-between text-xs">
          {result.calculation_id ? (
            <div className="flex items-center gap-1.5 text-emerald-700 font-medium">
              <Bookmark className="w-3.5 h-3.5" />
              <span>Збережено в історії вашого акаунту (ID #{result.calculation_id})</span>
            </div>
          ) : (
            <div className="flex items-center justify-between w-full">
              <span className="text-slate-500">
                Розрахунок не збережено (ви не увійшли в акаунт)
              </span>
              {onOpenAuth && (
                <button
                  onClick={onOpenAuth}
                  className="inline-flex items-center gap-1 py-1.5 px-1 -my-1.5 font-semibold text-blue-600 hover:text-blue-700 hover:underline"
                >
                  <LogIn className="w-3.5 h-3.5" />
                  Увійти
                </button>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
