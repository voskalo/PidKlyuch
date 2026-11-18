import React from 'react';
import { Heart, ShieldCheck, Scale, ExternalLink } from 'lucide-react';

interface FooterProps {
  onOpenDonation: () => void;
  onOpenStats: () => void;
}

export const Footer: React.FC<FooterProps> = ({ onOpenDonation, onOpenStats }) => {
  return (
    <footer className="bg-white border-t border-slate-200 mt-16 text-xs text-slate-500 py-12">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 space-y-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Col 1 */}
          <div className="md:col-span-2 space-y-3">
            <div className="flex items-center gap-2">
              <span className="font-extrabold text-slate-900 text-base">
                Під Ключ (PidKlyuch)
              </span>
              <span className="text-[10px] font-bold bg-blue-100 text-blue-700 px-1.5 py-0.5 rounded uppercase">
                v1.0 MVP
              </span>
            </div>
            <p className="text-slate-600 leading-relaxed text-xs">
              Веб-калькулятор розмитнення товарів та автомобілів, що імпортуються в Україну. Розраховує мито, ПДВ, акцизний податок та повну вартість покупки «під ключ» з відкритими формулами та офіційним курсом НБУ.
            </p>
            <div className="flex items-center gap-2 text-slate-400 text-[11px]">
              <Scale className="w-3.5 h-3.5 text-blue-600 shrink-0" />
              <span>Базується на МКУ ст. 374, ПКУ ст. 215 та Законах № 5025-IX / 5026-IX.</span>
            </div>
          </div>

          {/* Col 2 */}
          <div className="space-y-2">
            <h5 className="font-bold text-slate-900 uppercase tracking-wider text-[11px]">
              Корисні посилання
            </h5>
            <ul className="space-y-0.5">
              <li>
                <a
                  href="https://zakon.rada.gov.ua/laws/show/4495-17#Text"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:text-blue-600 transition-colors flex items-center gap-1 py-1"
                >
                  Митний кодекс України
                  <ExternalLink className="w-3 h-3 opacity-60" />
                </a>
              </li>
              <li>
                <a
                  href="https://zakon.rada.gov.ua/laws/show/2755-17#Text"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:text-blue-600 transition-colors flex items-center gap-1 py-1"
                >
                  Податковий кодекс України
                  <ExternalLink className="w-3 h-3 opacity-60" />
                </a>
              </li>
              <li>
                <a
                  href="https://bank.gov.ua/"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:text-blue-600 transition-colors flex items-center gap-1 py-1"
                >
                  Національний банк України
                  <ExternalLink className="w-3 h-3 opacity-60" />
                </a>
              </li>
            </ul>
          </div>

          {/* Col 3 */}
          <div className="space-y-2">
            <h5 className="font-bold text-slate-900 uppercase tracking-wider text-[11px]">
              Про проєкт
            </h5>
            <ul className="space-y-0.5">
              <li>
                <button
                  onClick={onOpenStats}
                  className="hover:text-blue-600 transition-colors py-1"
                >
                  Статистика використання
                </button>
              </li>
              <li>
                <button
                  onClick={onOpenDonation}
                  className="text-amber-700 hover:text-amber-800 font-medium flex items-center gap-1 py-1"
                >
                  <Heart className="w-3 h-3 text-rose-500 fill-current" />
                  Підтримати ЗСУ (Донат)
                </button>
              </li>
              <li className="text-slate-400 text-[11px] pt-1">
                Команда: Любомир Воськало, Анна Кравченко, Антон Вертипорох
              </li>
            </ul>
          </div>
        </div>

        <div className="pt-6 border-t border-slate-200 flex flex-col sm:flex-row items-center justify-between gap-3 text-slate-400 text-[11px]">
          <div className="flex items-center gap-1.5">
            <ShieldCheck className="w-4 h-4 text-emerald-600" />
            <span>Ставки верифіковано 16.11.2026. Розрахунки носять інформаційний характер.</span>
          </div>
          <div>
            PidKlyuch © 2026 • УКУ, 2 курс, ООАД
          </div>
        </div>
      </div>
    </footer>
  );
};
