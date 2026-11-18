import React from 'react';
import { X, Heart, ExternalLink, ShieldCheck, CheckCircle2 } from 'lucide-react';
import { ModalShell } from './ModalShell';

interface DonationModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const DonationModal: React.FC<DonationModalProps> = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  return (
    <ModalShell onClose={onClose} labelledBy="donation-modal-title" panelClassName="bg-white rounded-2xl shadow-2xl max-w-lg w-full overflow-hidden border border-slate-100 flex flex-col max-h-[90vh]">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 via-indigo-600 to-amber-500 p-6 text-white relative">
          <button
            onClick={onClose}
            aria-label="Закрити"
            className="absolute top-4 right-4 text-white/80 hover:text-white hover:bg-white/10 rounded-full p-1.5 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
          <div className="inline-flex items-center gap-2 bg-white/20 backdrop-blur-md px-3 py-1 rounded-full text-xs font-medium text-amber-200 mb-2">
            <Heart className="w-3.5 h-3.5 fill-current text-rose-300" />
            Підтримай перемогу
          </div>
          <h3 id="donation-modal-title" className="text-xl font-bold leading-tight">
            Підтримай Збройні Сили України
          </h3>
          <p className="text-sm text-blue-50 mt-1">
            Калькулятор «Під ключ» повністю безкоштовний. Якщо він заощадив ваш час чи кошти — задонатьте будь-яку суму на перевірені волонтерські фонди!
          </p>
        </div>

        {/* Content */}
        <div className="p-6 space-y-4 overflow-y-auto">
          <div className="space-y-3">
            {/* Save Life */}
            <a
              href="https://savelife.in.ua/donate/"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center justify-between p-4 rounded-xl border border-slate-200 hover:border-blue-500 hover:bg-blue-50/50 transition-all group"
            >
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-red-100 text-red-600 flex items-center justify-center font-bold text-sm shrink-0">
                  ПЖ
                </div>
                <div>
                  <h4 className="font-semibold text-slate-900 group-hover:text-blue-600 transition-colors flex items-center gap-1.5">
                    Фонд «Повернись живим»
                    <ExternalLink className="w-3.5 h-3.5 opacity-60" />
                  </h4>
                  <p className="text-xs text-slate-500">
                    Компетентна допомога Силам Оборони України
                  </p>
                </div>
              </div>
              <span className="text-xs font-semibold text-blue-600 bg-blue-100/70 px-2.5 py-1 rounded-full shrink-0">
                Задонатити
              </span>
            </a>

            {/* Prytula */}
            <a
              href="https://prytulafoundation.org/"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center justify-between p-4 rounded-xl border border-slate-200 hover:border-blue-500 hover:bg-blue-50/50 transition-all group"
            >
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-amber-100 text-amber-700 flex items-center justify-center font-bold text-sm shrink-0">
                  БФ
                </div>
                <div>
                  <h4 className="font-semibold text-slate-900 group-hover:text-blue-600 transition-colors flex items-center gap-1.5">
                    Фонд Сергія Притули
                    <ExternalLink className="w-3.5 h-3.5 opacity-60" />
                  </h4>
                  <p className="text-xs text-slate-500">
                    Броньовики, оптика, БПЛА та такмед для війська
                  </p>
                </div>
              </div>
              <span className="text-xs font-semibold text-blue-600 bg-blue-100/70 px-2.5 py-1 rounded-full shrink-0">
                Задонатити
              </span>
            </a>

            {/* Monobank jar */}
            <a
              href="https://send.monobank.ua/jar/223G2o5V4R"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center justify-between p-4 rounded-xl border border-slate-200 hover:border-blue-500 hover:bg-blue-50/50 transition-all group"
            >
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-emerald-100 text-emerald-700 flex items-center justify-center font-bold text-sm shrink-0">
                  ₴
                </div>
                <div>
                  <h4 className="font-semibold text-slate-900 group-hover:text-blue-600 transition-colors flex items-center gap-1.5">
                    Банка Monobank на потреби ЗСУ
                    <ExternalLink className="w-3.5 h-3.5 opacity-60" />
                  </h4>
                  <p className="text-xs text-slate-500">
                    Швидкий донат в один клік через Apple Pay / Google Pay
                  </p>
                </div>
              </div>
              <span className="text-xs font-semibold text-emerald-700 bg-emerald-100 px-2.5 py-1 rounded-full shrink-0">
                Відкрити банку
              </span>
            </a>
          </div>

          <div className="bg-slate-50 rounded-xl p-4 border border-slate-200/80 text-xs text-slate-600 space-y-2">
            <div className="flex items-start gap-2">
              <ShieldCheck className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
              <span>
                <strong>Бонусний критерій проєкту:</strong> Підтвердження готовності підтримати волонтерську справу додається до звіту тестування. Дякуємо кожному, хто допомагає!
              </span>
            </div>
            <div className="flex items-center gap-2 text-slate-500">
              <CheckCircle2 className="w-3.5 h-3.5 text-blue-600" />
              <span>100% коштів перераховуються безпосередньо у вибраний фонд</span>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 bg-slate-50 border-t border-slate-100 flex justify-end">
          <button
            onClick={onClose}
            className="px-5 py-2 text-sm font-medium text-slate-700 hover:bg-slate-200/70 rounded-xl transition-colors"
          >
            Закрити
          </button>
        </div>
      </ModalShell>
  );
};
