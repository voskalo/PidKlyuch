import React from 'react';
import { useAuth } from '../context/AuthContext';
import {
  KeyRound,
  Calculator,
  History,
  BarChart2,
  Heart,
  LogIn,
  LogOut,
  User as UserIcon,
} from 'lucide-react';

interface NavbarProps {
  currentTab: 'calculator' | 'history';
  onSelectTab: (tab: 'calculator' | 'history') => void;
  onOpenAuth: (mode?: 'signin' | 'signup') => void;
  onOpenDonation: () => void;
  onOpenStats: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  currentTab,
  onSelectTab,
  onOpenAuth,
  onOpenDonation,
  onOpenStats,
}) => {
  const { user, signout } = useAuth();

  return (
    <header className="bg-white border-b border-slate-200/80 sticky top-0 z-40 backdrop-blur-md bg-white/95 w-full overflow-x-hidden">
      <div className="max-w-6xl mx-auto px-3 sm:px-6">
        {/* Top bar: Brand + Actions */}
        <div className="h-14 sm:h-16 flex items-center justify-between gap-2 sm:gap-4">
          {/* Brand logo */}
          <div
            onClick={() => onSelectTab('calculator')}
            className="flex items-center gap-2 cursor-pointer select-none group shrink-0"
          >
            <div className="w-8 h-8 sm:w-10 sm:h-10 rounded-xl bg-gradient-to-tr from-blue-700 to-indigo-600 text-white flex items-center justify-center shadow-md shadow-blue-600/20 group-hover:scale-105 transition-transform shrink-0">
              <KeyRound className="w-4 h-4 sm:w-5 sm:h-5" />
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <span className="font-extrabold text-slate-900 text-base sm:text-lg tracking-tight">
                  Під Ключ
                </span>
                <span className="text-[10px] font-bold bg-blue-100 text-blue-700 px-1.5 py-0.5 rounded uppercase hidden xs:inline">
                  MVP
                </span>
              </div>
              <p className="text-[11px] text-slate-500 hidden sm:block">
                Калькулятор розмитнення товарів та авто
              </p>
            </div>
          </div>

          {/* Center navigation tabs (desktop only) */}
          <nav className="hidden lg:flex items-center gap-1 bg-slate-100 p-1 rounded-xl">
            <button
              onClick={() => onSelectTab('calculator')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                currentTab === 'calculator'
                  ? 'bg-white text-blue-600 shadow-sm'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              <Calculator className="w-4 h-4" />
              <span>Калькулятор</span>
            </button>

            <button
              onClick={() => {
                if (!user) {
                  onOpenAuth('signin');
                } else {
                  onSelectTab('history');
                }
              }}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                currentTab === 'history'
                  ? 'bg-white text-blue-600 shadow-sm'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              <History className="w-4 h-4" />
              <span>Історія</span>
            </button>
          </nav>

          {/* Right action area */}
          <div className="flex items-center gap-1.5 sm:gap-2 shrink-0">
            {/* Stats button */}
            <button
              onClick={onOpenStats}
              title="Статистика використання"
              className="p-2 text-slate-500 hover:text-slate-900 hover:bg-slate-100 rounded-xl transition-colors hidden sm:flex items-center gap-1 text-xs font-medium"
            >
              <BarChart2 className="w-4 h-4" />
              <span className="hidden lg:inline">Метрики</span>
            </button>

            {/* Donation button */}
            <button
              onClick={onOpenDonation}
              title="Підтримати ЗСУ"
              className="flex items-center gap-1 px-2.5 py-1.5 sm:px-3 bg-gradient-to-r from-amber-500 to-rose-500 hover:from-amber-600 hover:to-rose-600 text-white font-semibold text-xs rounded-xl shadow-sm transition-all"
            >
              <Heart className="w-3.5 h-3.5 fill-current shrink-0" />
              <span className="hidden sm:inline">Донат ЗСУ</span>
            </button>

            {/* User state */}
            {user ? (
              <div className="flex items-center gap-1.5 pl-1.5 sm:pl-2 border-l border-slate-200">
                <div className="flex items-center gap-1 px-2 py-1 bg-slate-100 rounded-xl text-xs font-medium text-slate-700 max-w-[90px] sm:max-w-[140px] truncate">
                  <UserIcon className="w-3.5 h-3.5 text-blue-600 shrink-0" />
                  <span className="truncate">{user.name || user.email}</span>
                </div>
                <button
                  onClick={signout}
                  title="Вийти з акаунту"
                  className="p-1.5 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-xl transition-colors shrink-0"
                >
                  <LogOut className="w-4 h-4" />
                </button>
              </div>
            ) : (
              <div className="flex items-center gap-1 pl-1.5 sm:pl-2 border-l border-slate-200">
                <button
                  onClick={() => onOpenAuth('signin')}
                  className="px-2.5 py-1.5 sm:px-3 text-xs font-semibold text-slate-700 hover:text-slate-900 hover:bg-slate-100 rounded-xl transition-colors flex items-center gap-1 shrink-0"
                >
                  <LogIn className="w-3.5 h-3.5" />
                  <span>Увійти</span>
                </button>
                <button
                  onClick={() => onOpenAuth('signup')}
                  className="px-3 py-1.5 text-xs font-semibold text-white bg-blue-600 hover:bg-blue-700 rounded-xl transition-colors hidden sm:block shadow-sm"
                >
                  Реєстрація
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Bottom tab bar (mobile only, < md) */}
        <div className="pb-2.5 pt-0.5 lg:hidden">
          <nav className="flex items-center gap-1 bg-slate-100 p-1 rounded-xl w-full">
            <button
              onClick={() => onSelectTab('calculator')}
              className={`flex-1 flex items-center justify-center gap-1.5 py-1.5 rounded-lg text-xs font-bold transition-all ${
                currentTab === 'calculator'
                  ? 'bg-white text-blue-600 shadow-sm'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              <Calculator className="w-3.5 h-3.5" />
              <span>Калькулятор</span>
            </button>

            <button
              onClick={() => {
                if (!user) {
                  onOpenAuth('signin');
                } else {
                  onSelectTab('history');
                }
              }}
              className={`flex-1 flex items-center justify-center gap-1.5 py-1.5 rounded-lg text-xs font-bold transition-all ${
                currentTab === 'history'
                  ? 'bg-white text-blue-600 shadow-sm'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              <History className="w-3.5 h-3.5" />
              <span>Історія</span>
            </button>
          </nav>
        </div>
      </div>
    </header>
  );
};
