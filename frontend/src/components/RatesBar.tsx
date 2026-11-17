import React, { useEffect, useState } from 'react';
import type { RatesResponse } from '../types/api';
import { api } from '../services/api';
import { RefreshCw, TrendingUp, AlertTriangle } from 'lucide-react';

export const RatesBar: React.FC = () => {
  const [rates, setRates] = useState<RatesResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchRates = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.getRates();
      setRates(data);
    } catch {
      setError('Не вдалося завантажити курси');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRates();
  }, []);

  if (error && !rates) {
    return null;
  }

  return (
    <div className="bg-slate-900 text-slate-200 text-xs py-2 px-4 border-b border-slate-800">
      <div className="max-w-6xl mx-auto flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <TrendingUp className="w-4 h-4 text-emerald-400 shrink-0" />
          <span className="font-medium text-slate-300">
            {rates?.source === 'nbu' ? 'Офіційні курси НБУ' : 'Резервні курси'}
          </span>
          {rates?.date && (
            <span className="text-slate-400">({rates.date})</span>
          )}
          {rates?.source === 'fallback' && (
            <span className="inline-flex items-center gap-1 text-amber-400 bg-amber-400/10 px-1.5 py-0.5 rounded text-[11px]">
              <AlertTriangle className="w-3 h-3" />
              офлайн-режим
            </span>
          )}
        </div>

        <div className="flex items-center flex-wrap gap-4">
          {rates?.uah_per_unit && (
            <>
              <div className="flex items-center gap-1.5">
                <span className="text-slate-400">1 EUR =</span>
                <span className="font-semibold text-white">
                  {parseFloat(rates.uah_per_unit.EUR || '0').toFixed(2)} ₴
                </span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="text-slate-400">1 USD =</span>
                <span className="font-semibold text-white">
                  {parseFloat(rates.uah_per_unit.USD || '0').toFixed(2)} ₴
                </span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="text-slate-400">1 PLN =</span>
                <span className="font-semibold text-white">
                  {parseFloat(rates.uah_per_unit.PLN || '0').toFixed(2)} ₴
                </span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="text-slate-400">1 GBP =</span>
                <span className="font-semibold text-white">
                  {parseFloat(rates.uah_per_unit.GBP || '0').toFixed(2)} ₴
                </span>
              </div>
            </>
          )}

          <button
            onClick={fetchRates}
            disabled={loading}
            title="Оновити курси"
            className="text-slate-400 hover:text-white transition-colors p-1 rounded hover:bg-slate-800 disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>
    </div>
  );
};
