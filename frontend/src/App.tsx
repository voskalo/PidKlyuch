import React, { useEffect, useRef, useState } from 'react';
import { AuthProvider } from './context/AuthContext';
import { Navbar } from './components/Navbar';
import { RatesBar } from './components/RatesBar';
import { ParcelForm } from './components/ParcelForm';
import { CarForm } from './components/CarForm';
import { BreakdownView } from './components/BreakdownView';
import { HistoryView } from './components/HistoryView';
import { CompareRulesModal } from './components/CompareRulesModal';
import { AuthModal } from './components/AuthModal';
import { DonationModal } from './components/DonationModal';
import { StatsModal } from './components/StatsModal';
import { Footer } from './components/Footer';
import type {
  CalculateRequest,
  CalculationResult,
  CompareRulesResult,
  DeliveryType,
  ParcelCalculateRequest,
} from './types/api';
import { api } from './services/api';
import {
  Package,
  Car,
  CheckCircle2,
  AlertCircle,
  HelpCircle,
  Sparkles,
} from 'lucide-react';

const MainApp: React.FC = () => {
  const [currentTab, setCurrentTab] = useState<'calculator' | 'history'>('calculator');
  const [deliveryType, setDeliveryType] = useState<DeliveryType>('parcel');
  const [calculationResult, setCalculationResult] = useState<CalculationResult | null>(null);
  const [compareResult, setCompareResult] = useState<CompareRulesResult | null>(null);

  // Modals state
  const [authModalOpen, setAuthModalOpen] = useState(false);
  const [authMode, setAuthMode] = useState<'signin' | 'signup'>('signin');
  const [donationModalOpen, setDonationModalOpen] = useState(false);
  const [statsModalOpen, setStatsModalOpen] = useState(false);
  const [compareModalOpen, setCompareModalOpen] = useState(false);
  const [errorToast, setErrorToast] = useState<string | null>(null);
  // The parcel request behind the result on screen, so "Порівняти правила" compares THIS parcel.
  const [lastParcelRequest, setLastParcelRequest] = useState<ParcelCalculateRequest | null>(null);
  const [comparingFromResult, setComparingFromResult] = useState(false);
  const errorRef = useRef<HTMLDivElement | null>(null);
  const resultRef = useRef<HTMLDivElement | null>(null);

  // On phones the form is long: the error banner (top) and the result (below the form) are off-screen.
  useEffect(() => {
    if (errorToast) errorRef.current?.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }, [errorToast]);
  useEffect(() => {
    if (calculationResult && window.matchMedia('(max-width: 1023px)').matches) {
      resultRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }, [calculationResult]);

  const handleOpenAuth = (mode: 'signin' | 'signup' = 'signin') => {
    setAuthMode(mode);
    setAuthModalOpen(true);
  };

  const handleCalculated = (result: CalculationResult, request?: CalculateRequest) => {
    setCalculationResult(result);
    setLastParcelRequest(request?.delivery_type === 'parcel' ? request : null);
    setErrorToast(null);
  };

  const handleCompare = (comparison: CompareRulesResult) => {
    setCompareResult(comparison);
    setCompareModalOpen(true);
    setErrorToast(null);
  };

  const handleCompareFromResult = async () => {
    if (!lastParcelRequest || comparingFromResult) return;
    try {
      setComparingFromResult(true);
      const { rules: _ignored, ...body } = lastParcelRequest;
      handleCompare(await api.compareRules(body));
    } catch (err: unknown) {
      setErrorToast(err instanceof Error ? err.message : 'Не вдалося порівняти правила');
    } finally {
      setComparingFromResult(false);
    }
  };

  const handleError = (msg: string) => {
    setErrorToast(msg);
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-50 text-slate-900 font-sans w-full overflow-x-hidden max-w-full">
      {/* Top live currency rates ticker */}
      <RatesBar />

      {/* Main navigation */}
      <Navbar
        currentTab={currentTab}
        onSelectTab={(tab) => {
          setCurrentTab(tab);
          window.scrollTo({ top: 0, behavior: 'smooth' });
        }}
        onOpenAuth={handleOpenAuth}
        onOpenDonation={() => setDonationModalOpen(true)}
        onOpenStats={() => setStatsModalOpen(true)}
      />

      {/* Main Content */}
      <main className="flex-1 max-w-6xl w-full mx-auto px-3 sm:px-6 py-6 sm:py-8 overflow-x-hidden">
        {/* Error Toast */}
        {errorToast && (
          <div
            ref={errorRef}
            role="alert"
            className="mb-6 p-4 rounded-2xl bg-red-50 border border-red-200 text-red-700 flex items-center justify-between text-sm shadow-sm animate-in fade-in">
            <div className="flex items-center gap-2.5">
              <AlertCircle className="w-5 h-5 text-red-500 shrink-0" />
              <span>{errorToast}</span>
            </div>
            <button
              onClick={() => setErrorToast(null)}
              className="text-red-400 hover:text-red-700 font-bold px-2 py-1"
            >
              ✕
            </button>
          </div>
        )}

        {currentTab === 'history' ? (
          <HistoryView onGoToCalculator={() => setCurrentTab('calculator')} />
        ) : (
          <div className="space-y-8">
            {/* Hero Title */}
            <div className="text-center max-w-2xl mx-auto space-y-2">
              <div className="inline-flex items-center gap-2 bg-blue-50 border border-blue-200/80 px-3 py-1 rounded-full text-xs font-semibold text-blue-700">
                <Sparkles className="w-3.5 h-3.5 text-blue-600" />
                Прозорий розрахунок без прихованих платежів
              </div>
              <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-slate-900">
                Скільки коштує розмитнення «Під ключ»?
              </h1>
              <p className="text-sm sm:text-base text-slate-600">
                Оберіть тип імпорту, вкажіть вартість та дізнайтеся повну кінцеву ціну з точними формулами мита, акцизу та ПДВ за курсом НБУ.
              </p>
            </div>

            {/* Delivery type selector buttons */}
            <div className="flex justify-center">
              <div className="bg-slate-200/80 p-1.5 rounded-2xl flex items-center gap-1.5 max-w-md w-full shadow-inner">
                <button
                  type="button"
                  onClick={() => {
                    setDeliveryType('parcel');
                    setCalculationResult(null);
                  }}
                  className={`flex-1 py-3 px-4 rounded-xl font-bold text-sm flex items-center justify-center gap-2 transition-all ${
                    deliveryType === 'parcel'
                      ? 'bg-white text-blue-600 shadow-md scale-[1.02]'
                      : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  <Package className="w-4 h-4" />
                  <span>Посилки з-за кордону</span>
                </button>

                <button
                  type="button"
                  onClick={() => {
                    setDeliveryType('car');
                    setCalculationResult(null);
                  }}
                  className={`flex-1 py-3 px-4 rounded-xl font-bold text-sm flex items-center justify-center gap-2 transition-all ${
                    deliveryType === 'car'
                      ? 'bg-white text-blue-600 shadow-md scale-[1.02]'
                      : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  <Car className="w-4 h-4" />
                  <span>Розмитнення авто</span>
                </button>
              </div>
            </div>

            {/* Two-column layout: Form & Breakdown */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
              {/* Form container */}
              <div className="lg:col-span-6 bg-white p-6 sm:p-7 rounded-3xl border border-slate-200 shadow-sm space-y-6">
                <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                  <h2 className="font-bold text-slate-900 text-base flex items-center gap-2">
                    {deliveryType === 'parcel' ? (
                      <>
                        <Package className="w-5 h-5 text-blue-600" />
                        Параметри посилки
                      </>
                    ) : (
                      <>
                        <Car className="w-5 h-5 text-blue-600" />
                        Параметри автомобіля
                      </>
                    )}
                  </h2>

                  <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                    Крок за кроком
                  </span>
                </div>

                {deliveryType === 'parcel' ? (
                  <ParcelForm
                    onCalculated={handleCalculated}
                    onCompare={handleCompare}
                    onError={handleError}
                  />
                ) : (
                  <CarForm
                    onCalculated={handleCalculated}
                    onError={handleError}
                  />
                )}
              </div>

              {/* Breakdown or Pitch Placeholder container */}
              <div ref={resultRef} className="lg:col-span-6 scroll-mt-4">
                {calculationResult ? (
                  <BreakdownView
                    result={calculationResult}
                    onOpenAuth={() => handleOpenAuth('signin')}
                    onCompareRules={
                      deliveryType === 'parcel' && lastParcelRequest ? handleCompareFromResult : undefined
                    }
                  />
                ) : (
                  <div className="bg-white rounded-3xl border border-slate-200/90 p-6 sm:p-8 shadow-sm space-y-6">
                    <div>
                      <h3 className="font-bold text-slate-900 text-lg">
                        Чому правила розмитнення складні?
                      </h3>
                      <p className="text-xs text-slate-500 mt-1 leading-relaxed">
                        Українське митне законодавство має різні пороги, пільги та коефіцієнти віку, які суттєво змінюють фінальну суму:
                      </p>
                    </div>

                    <div className="space-y-4">
                      <div className="flex items-start gap-3 p-4 rounded-2xl bg-blue-50/60 border border-blue-100">
                        <CheckCircle2 className="w-5 h-5 text-blue-600 shrink-0 mt-0.5" />
                        <div className="text-xs space-y-1">
                          <strong className="text-blue-950 font-bold block">
                            Посилки: поріг €150 та зміни 2027 року
                          </strong>
                          <p className="text-slate-600 leading-relaxed">
                            Зараз товари до €150 ввозяться без податків. Якщо посилка на €200 — податки нараховуються лише на різницю (€50): мито 10% + ПДВ 20% = всього <strong>€16</strong>. Проте з липня 2027 обов'язковий ПДВ 20% діятиме від першого євро, а для посилок понад €150 мито й ПДВ рахуватимуться з усієї вартості (€200 → €64).
                          </p>
                        </div>
                      </div>

                      <div className="flex items-start gap-3 p-4 rounded-2xl bg-indigo-50/60 border border-indigo-100">
                        <CheckCircle2 className="w-5 h-5 text-indigo-600 shrink-0 mt-0.5" />
                        <div className="text-xs space-y-1">
                          <strong className="text-indigo-950 font-bold block">
                            Автомобілі: формула акцизу та походження
                          </strong>
                          <p className="text-slate-600 leading-relaxed">
                            Акциз на авто рахується за формулою: <em>Базова ставка × Коеф. об'єму × Коеф. віку</em>. Наприклад, для авто на €10 000 податки можуть скласти як <strong>€2 048</strong> (нове авто з ЄС), так і <strong>€4 640</strong> (12-річне авто не з ЄС).
                          </p>
                        </div>
                      </div>

                      <div className="flex items-start gap-3 p-4 rounded-2xl bg-emerald-50/60 border border-emerald-100">
                        <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0 mt-0.5" />
                        <div className="text-xs space-y-1">
                          <strong className="text-emerald-950 font-bold block">
                            Офіційний курс НБУ щодня
                          </strong>
                          <p className="text-slate-600 leading-relaxed">
                            Усі митні платежі в Україні сплачуються виключно у гривні за офіційним курсом НБУ на день оформлення. PidKlyuch підтягує свіжі курси щогодини.
                          </p>
                        </div>
                      </div>
                    </div>

                    <div className="p-4 bg-slate-50 rounded-2xl border border-slate-200 flex items-center gap-2.5 text-xs text-slate-500">
                      <HelpCircle className="w-4 h-4 text-slate-400 shrink-0" />
                      <span>
                        Заповніть поля зліва та натисніть «Розрахувати», щоб отримати персональний розрахунок із відкритими формулами.
                      </span>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Modals */}
      <AuthModal
        isOpen={authModalOpen}
        onClose={() => setAuthModalOpen(false)}
        initialMode={authMode}
      />

      <DonationModal
        isOpen={donationModalOpen}
        onClose={() => setDonationModalOpen(false)}
      />

      <StatsModal
        isOpen={statsModalOpen}
        onClose={() => setStatsModalOpen(false)}
      />

      <CompareRulesModal
        isOpen={compareModalOpen}
        onClose={() => setCompareModalOpen(false)}
        comparison={compareResult}
      />

      {/* Footer */}
      <Footer
        onOpenDonation={() => setDonationModalOpen(true)}
        onOpenStats={() => setStatsModalOpen(true)}
      />
    </div>
  );
};

export const App: React.FC = () => {
  return (
    <AuthProvider>
      <MainApp />
    </AuthProvider>
  );
};

export default App;
