import React, { useEffect, useState } from 'react';
import type { HistoryItem } from '../types/api';
import { api } from '../services/api';
import {
  History,
  Trash2,
  Package,
  Car,
  ChevronDown,
  ChevronUp,
  Loader2,
  AlertCircle,
  Calendar,
} from 'lucide-react';
import { BreakdownView } from './BreakdownView';

interface HistoryViewProps {
  onGoToCalculator: () => void;
}

export const HistoryView: React.FC<HistoryViewProps> = ({ onGoToCalculator }) => {
  const [items, setItems] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedId, setExpandedId] = useState<number | null>(null);
  const [deletingId, setDeletingId] = useState<number | null>(null);

  const fetchHistory = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.getHistory();
      setItems(data);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Не вдалося завантажити історію');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const handleDelete = async (id: number, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm('Ви дійсно хочете видалити цей розрахунок з історії?')) {
      return;
    }

    try {
      setDeletingId(id);
      await api.deleteHistory(id);
      setItems((prev) => prev.filter((item) => item.id !== id));
      if (expandedId === id) {
        setExpandedId(null);
      }
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : 'Не вдалося видалити запис');
    } finally {
      setDeletingId(null);
    }
  };

  const toggleExpand = (id: number) => {
    setExpandedId(expandedId === id ? null : id);
  };

  if (loading) {
    return (
      <div className="py-20 flex flex-col items-center justify-center text-slate-400 gap-3">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
        <span className="text-sm font-medium">Завантаження історії розрахунків...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 bg-red-50 border border-red-200 rounded-2xl text-center space-y-3 max-w-md mx-auto">
        <AlertCircle className="w-8 h-8 text-red-500 mx-auto" />
        <h4 className="font-bold text-red-900 text-sm">{error}</h4>
        <button
          onClick={fetchHistory}
          className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-xl text-xs font-semibold"
        >
          Спробувати знову
        </button>
      </div>
    );
  }

  if (items.length === 0) {
    return (
      <div className="py-16 px-4 text-center max-w-md mx-auto space-y-4">
        <div className="w-16 h-16 rounded-full bg-blue-50 text-blue-600 flex items-center justify-center mx-auto">
          <History className="w-8 h-8" />
        </div>
        <div>
          <h3 className="font-bold text-slate-900 text-lg">
            У вас ще немає збережених розрахунків
          </h3>
          <p className="text-xs text-slate-500 mt-1">
            Кожен розрахунок, зроблений під час входу в акаунт, автоматично зберігається тут.
          </p>
        </div>
        <button
          onClick={onGoToCalculator}
          className="px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs rounded-xl shadow-md transition-colors"
        >
          Зробити перший розрахунок
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between pb-3 border-b border-slate-200">
        <div>
          <h3 className="font-bold text-slate-900 text-lg flex items-center gap-2">
            <History className="w-5 h-5 text-blue-600" />
            Історія розрахунків
          </h3>
          <p className="text-xs text-slate-500">
            Збережено записів: {items.length}
          </p>
        </div>
      </div>

      <div className="space-y-3">
        {items.map((item) => {
          const isCar = item.delivery_type === 'car';
          const isExpanded = expandedId === item.id;
          const isDeleting = deletingId === item.id;
          const dateStr = new Date(item.created_at).toLocaleString('uk-UA', {
            day: 'numeric',
            month: 'long',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
          });

          return (
            <div
              key={item.id}
              className="bg-white rounded-2xl border border-slate-200/90 shadow-sm overflow-hidden transition-all hover:border-slate-300"
            >
              {/* Item summary bar */}
              <div
                onClick={() => toggleExpand(item.id)}
                className="p-4 sm:p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-3 cursor-pointer select-none"
              >
                <div className="flex items-start sm:items-center gap-3">
                  <div className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0 ${
                    isCar
                      ? 'bg-purple-100 text-purple-700'
                      : 'bg-blue-100 text-blue-700'
                  }`}>
                    {isCar ? <Car className="w-5 h-5" /> : <Package className="w-5 h-5" />}
                  </div>

                  <div>
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="font-bold text-slate-900 text-sm">
                        {isCar ? 'Розмитнення автомобіля' : 'Розмитнення посилки'}
                      </span>
                      <span className="text-[11px] font-medium text-slate-400 flex items-center gap-1">
                        <Calendar className="w-3 h-3" />
                        {dateStr}
                      </span>
                    </div>

                    <div className="text-xs text-slate-500 mt-0.5">
                      {isCar ? (
                        <>
                          Ціна: {String(item.input.car_price || '')} {String(item.input.currency || 'EUR')} • Двигун:{' '}
                          {String(item.input.engine_type || '')} • Рік: {String(item.input.manufacture_year || '')}
                        </>
                      ) : (
                        <>
                          Ціна товару: {String(item.input.item_price || '')} {String(item.input.currency || 'EUR')}
                        </>
                      )}
                    </div>
                  </div>
                </div>

                <div className="flex items-center justify-between sm:justify-end gap-4 shrink-0 pt-2 sm:pt-0 border-t sm:border-0 border-slate-100">
                  <div className="text-left sm:text-right">
                    <div className="text-base font-bold text-slate-900">
                      {item.result.landed_total_uah} ₴
                    </div>
                    <div className="text-[11px] text-slate-400">
                      податки: {item.result.taxes_total_uah} ₴
                    </div>
                  </div>

                  <div className="flex items-center gap-1">
                    <button
                      type="button"
                      onClick={(e) => handleDelete(item.id, e)}
                      disabled={isDeleting}
                      title="Видалити розрахунок"
                      className="p-2 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-xl transition-colors disabled:opacity-50"
                    >
                      {isDeleting ? (
                        <Loader2 className="w-4 h-4 animate-spin text-red-600" />
                      ) : (
                        <Trash2 className="w-4 h-4" />
                      )}
                    </button>

                    <button
                      type="button"
                      aria-label={isExpanded ? "Згорнути деталі" : "Розгорнути деталі"}
                      className="p-2 text-slate-400 hover:text-slate-700 hover:bg-slate-100 rounded-xl transition-colors"
                    >
                      {isExpanded ? (
                        <ChevronUp className="w-4 h-4" />
                      ) : (
                        <ChevronDown className="w-4 h-4" />
                      )}
                    </button>
                  </div>
                </div>
              </div>

              {/* Expanded breakdown */}
              {isExpanded && (
                <div className="p-4 sm:p-5 bg-slate-50/70 border-t border-slate-100">
                  <BreakdownView result={item.result} />
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
