import React, { useEffect, useState } from 'react';
import { X, Users, Calculator, UserCheck, BarChart3, RefreshCw } from 'lucide-react';
import { ModalShell } from './ModalShell';
import type { StatsResponse } from '../types/api';
import { api } from '../services/api';

interface StatsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const StatsModal: React.FC<StatsModalProps> = ({ isOpen, onClose }) => {
  const [stats, setStats] = useState<StatsResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchStats = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.getStats();
      setStats(data);
    } catch {
      setError('Не вдалося завантажити статистику');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchStats();
    }
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <ModalShell onClose={onClose} labelledBy="stats-modal-title" panelClassName="bg-white rounded-2xl shadow-2xl max-w-md w-full max-h-[calc(100dvh-2rem)] overflow-y-auto overscroll-contain border border-slate-100">
        <div className="flex items-center justify-between p-5 border-b border-slate-100 bg-slate-50/70">
          <div className="flex items-center gap-2">
            <BarChart3 className="w-5 h-5 text-blue-600" />
            <h3 id="stats-modal-title" className="font-bold text-slate-900 text-base">
              Метрики використання проєкту
            </h3>
          </div>
          <button
            onClick={onClose}
            aria-label="Закрити"
            className="text-slate-400 hover:text-slate-600 p-1 rounded-full hover:bg-slate-200/50 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-6 space-y-4">
          <p className="text-xs text-slate-500 leading-relaxed">
            Дані збираються для підсумкового звіту тестування продукту (активність користувачів, кількість розрахунків та ретеншн).
          </p>

          {loading ? (
            <div className="py-12 flex flex-col items-center justify-center text-slate-400 gap-2">
              <RefreshCw className="w-6 h-6 animate-spin text-blue-600" />
              <span className="text-xs">Завантаження показників...</span>
            </div>
          ) : error ? (
            <div className="p-4 rounded-xl bg-red-50 text-red-600 text-xs">
              {error}
            </div>
          ) : (
            <div className="grid grid-cols-1 min-[360px]:grid-cols-2 gap-3">
              <div className="p-4 rounded-xl bg-blue-50/70 border border-blue-100">
                <div className="flex items-center justify-between text-blue-600 mb-1">
                  <span className="text-xs font-semibold">Розрахунків</span>
                  <Calculator className="w-4 h-4" />
                </div>
                <div className="text-2xl font-bold text-slate-900">
                  {stats?.calculations ?? 0}
                </div>
                <div className="text-[11px] text-slate-500 mt-1">
                  всіх запитів landed cost
                </div>
              </div>

              <div className="p-4 rounded-xl bg-indigo-50/70 border border-indigo-100">
                <div className="flex items-center justify-between text-indigo-600 mb-1">
                  <span className="text-xs font-semibold">Користувачів</span>
                  <Users className="w-4 h-4" />
                </div>
                <div className="text-2xl font-bold text-slate-900">
                  {stats?.users ?? 0}
                </div>
                <div className="text-[11px] text-slate-500 mt-1">
                  зареєстрованих акаунтів
                </div>
              </div>

              <div className="p-4 rounded-xl bg-emerald-50/70 border border-emerald-100">
                <div className="flex items-center justify-between text-emerald-600 mb-1">
                  <span className="text-xs font-semibold">Авторизованих</span>
                  <UserCheck className="w-4 h-4" />
                </div>
                <div className="text-2xl font-bold text-slate-900">
                  {stats?.calculations_by_signed_in ?? 0}
                </div>
                <div className="text-[11px] text-slate-500 mt-1">
                  розрахунків збережено
                </div>
              </div>

              <div className="p-4 rounded-xl bg-amber-50/70 border border-amber-100">
                <div className="flex items-center justify-between text-amber-600 mb-1">
                  <span className="text-xs font-semibold">Returning</span>
                  <BarChart3 className="w-4 h-4" />
                </div>
                <div className="text-2xl font-bold text-slate-900">
                  {stats?.returning_users ?? 0}
                </div>
                <div className="text-[11px] text-slate-500 mt-1">
                  користувачі 2+ днів
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="p-4 bg-slate-50 border-t border-slate-100 flex justify-between items-center">
          <button
            onClick={fetchStats}
            disabled={loading}
            className="inline-flex items-center gap-1.5 text-xs text-slate-600 hover:text-slate-900 font-medium px-3 py-1.5 rounded-lg hover:bg-slate-200/50 transition-colors"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            Оновити
          </button>
          <button
            onClick={onClose}
            className="px-4 py-1.5 text-xs font-medium text-slate-700 bg-white border border-slate-200 hover:bg-slate-50 rounded-xl transition-colors shadow-sm"
          >
            Закрити
          </button>
        </div>
      </ModalShell>
  );
};
