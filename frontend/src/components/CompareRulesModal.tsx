import React from 'react';
import { X, AlertTriangle, ShieldCheck } from 'lucide-react';
import type { CompareRulesResult } from '../types/api';

interface CompareRulesModalProps {
  isOpen: boolean;
  onClose: () => void;
  comparison: CompareRulesResult | null;
}

export const CompareRulesModal: React.FC<CompareRulesModalProps> = ({
  isOpen,
  onClose,
  comparison,
}) => {
  if (!isOpen || !comparison) return null;

  const { current, july_2027 } = comparison;

  const currentTaxEur = parseFloat(current.taxes_total_eur);
  const julyTaxEur = parseFloat(july_2027.taxes_total_eur);
  const diffTaxEur = julyTaxEur - currentTaxEur;

  const currentTaxUah = parseFloat(current.taxes_total_uah);
  const julyTaxUah = parseFloat(july_2027.taxes_total_uah);
  const diffTaxUah = julyTaxUah - currentTaxUah;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full overflow-hidden border border-slate-100 flex flex-col max-h-[90vh]">
        {/* Header */}
        <div className="flex items-center justify-between p-5 border-b border-slate-100 bg-slate-50">
          <div>
            <div className="inline-flex items-center gap-1.5 bg-blue-100 text-blue-700 text-xs px-2.5 py-0.5 rounded-full font-semibold mb-1">
              Закони № 5025-IX / 5026-IX
            </div>
            <h3 className="font-bold text-slate-900 text-lg">
              Порівняння правил: Зараз vs Липень 2027
            </h3>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-600 p-1 rounded-full hover:bg-slate-200/50 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Comparison body */}
        <div className="p-6 overflow-y-auto space-y-6">
          {/* Summary difference badge */}
          <div className={`p-4 rounded-xl border flex items-center justify-between gap-4 ${
            diffTaxEur > 0
              ? 'bg-amber-50 border-amber-200 text-amber-900'
              : 'bg-emerald-50 border-emerald-200 text-emerald-900'
          }`}>
            <div className="flex items-center gap-3">
              {diffTaxEur > 0 ? (
                <AlertTriangle className="w-6 h-6 text-amber-600 shrink-0" />
              ) : (
                <ShieldCheck className="w-6 h-6 text-emerald-600 shrink-0" />
              )}
              <div>
                <h4 className="font-bold text-sm">
                  {diffTaxEur > 0
                    ? `Податок зросте на +${diffTaxEur.toFixed(2)} € (+${diffTaxUah.toFixed(2)} ₴)`
                    : 'Сума податків не зміниться'}
                </h4>
                <p className="text-xs opacity-80 mt-0.5">
                  {diffTaxEur > 0
                    ? 'Через скасування безмитного порогу ПДВ для комерційних посилок з липня 2027 року.'
                    : 'Для цієї вартості посилки податкові правила залишаються аналогічними.'}
                </p>
              </div>
            </div>
          </div>

          {/* Side by side comparison cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Current */}
            <div className="border border-slate-200 rounded-xl p-4 bg-slate-50/50 space-y-3">
              <div className="flex items-center justify-between pb-2 border-b border-slate-200">
                <span className="font-bold text-slate-800 text-sm">Зараз (Поточні правила)</span>
                <span className="text-[11px] font-semibold bg-slate-200 text-slate-700 px-2 py-0.5 rounded">
                  МКУ ст. 374
                </span>
              </div>

              <div className="space-y-1.5 text-xs">
                <div className="flex justify-between text-slate-600">
                  <span>Безмитний поріг:</span>
                  <span className="font-semibold text-slate-900">до €150 без податків</span>
                </div>
                <div className="flex justify-between text-slate-600">
                  <span>Оподаткування:</span>
                  <span className="font-semibold text-slate-900">Тільки на перевищення €150</span>
                </div>
              </div>

              <div className="pt-2 border-t border-slate-200">
                <div className="text-xs text-slate-500">Податки разом:</div>
                <div className="text-xl font-bold text-slate-900">
                  {current.taxes_total_uah} ₴
                  <span className="text-xs text-slate-500 font-normal ml-1.5">
                    ({current.taxes_total_eur} €)
                  </span>
                </div>
                <div className="text-xs text-slate-600 mt-1">
                  Разом під ключ: <strong className="text-slate-900">{current.landed_total_uah} ₴</strong>
                </div>
              </div>

              {/* Lines */}
              <div className="pt-2 border-t border-slate-200/80 space-y-1 text-xs">
                {current.lines.length === 0 ? (
                  <div className="text-emerald-700 bg-emerald-50 p-2 rounded text-center font-medium">
                    Податки відсутні (до €150)
                  </div>
                ) : (
                  current.lines.map((line) => (
                    <div key={line.code} className="flex justify-between text-slate-700">
                      <span>{line.label}:</span>
                      <span className="font-medium">{line.amount_uah} ₴ ({line.amount_eur} €)</span>
                    </div>
                  ))
                )}
              </div>
            </div>

            {/* July 2027 */}
            <div className="border border-blue-200 rounded-xl p-4 bg-blue-50/30 space-y-3">
              <div className="flex items-center justify-between pb-2 border-b border-blue-100">
                <span className="font-bold text-blue-900 text-sm">З липня 2027 року</span>
                <span className="text-[11px] font-semibold bg-blue-100 text-blue-700 px-2 py-0.5 rounded">
                  Закон 5025-IX
                </span>
              </div>

              <div className="space-y-1.5 text-xs">
                <div className="flex justify-between text-slate-600">
                  <span>Поріг для ПДВ:</span>
                  <span className="font-semibold text-blue-900">Скасовано (ПДВ 20% від €0)</span>
                </div>
                <div className="flex justify-between text-slate-600">
                  <span>Мито (10%):</span>
                  <span className="font-semibold text-slate-900">Лише на суму понад €150</span>
                </div>
              </div>

              <div className="pt-2 border-t border-blue-100">
                <div className="text-xs text-slate-500">Податки разом:</div>
                <div className="text-xl font-bold text-blue-900">
                  {july_2027.taxes_total_uah} ₴
                  <span className="text-xs text-blue-700 font-normal ml-1.5">
                    ({july_2027.taxes_total_eur} €)
                  </span>
                </div>
                <div className="text-xs text-slate-600 mt-1">
                  Разом під ключ: <strong className="text-blue-950">{july_2027.landed_total_uah} ₴</strong>
                </div>
              </div>

              {/* Lines */}
              <div className="pt-2 border-t border-blue-100/80 space-y-1 text-xs">
                {july_2027.lines.length === 0 ? (
                  <div className="text-emerald-700 bg-emerald-50 p-2 rounded text-center font-medium">
                    Податки відсутні (подарунок від фізособи до €45)
                  </div>
                ) : (
                  july_2027.lines.map((line) => (
                    <div key={line.code} className="flex justify-between text-slate-700">
                      <span>{line.label}:</span>
                      <span className="font-medium">{line.amount_uah} ₴ ({line.amount_eur} €)</span>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>

          <div className="bg-slate-50 rounded-xl p-4 border border-slate-200 text-xs text-slate-600 space-y-1.5">
            <h5 className="font-bold text-slate-800 flex items-center gap-1.5">
              💡 Що змінюється для покупців:
            </h5>
            <p>
              • <strong>Зараз:</strong> посилки до €150 не оподатковуються взагалі.
            </p>
            <p>
              • <strong>З липня 2027:</strong> обов’язковий ПДВ 20% нараховується на кожну комерційну посилку будь-якої вартості (сплачуватиметься безпосередньо маркетплейсом при оплаті).
            </p>
            <p>
              • Подарунки від приватних осіб без комерційної мети залишаються безмитними до <strong>€45</strong>.
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 bg-slate-50 border-t border-slate-100 flex justify-end">
          <button
            onClick={onClose}
            className="px-5 py-2 text-sm font-semibold text-white bg-blue-600 hover:bg-blue-700 rounded-xl transition-colors shadow-sm"
          >
            Зрозуміло
          </button>
        </div>
      </div>
    </div>
  );
};
