import React, { useEffect, useRef, useState } from 'react';
import { X, Mail, Lock, User as UserIcon, AlertCircle, Loader2 } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const GOOGLE_CLIENT_ID = (import.meta.env.VITE_GOOGLE_CLIENT_ID || '').trim();
const GOOGLE_GSI_SRC = 'https://accounts.google.com/gsi/client';

interface GoogleCredentialResponse {
  credential?: string;
}

interface GoogleAccountsId {
  initialize: (config: {
    client_id: string;
    callback: (response: GoogleCredentialResponse) => void;
    auto_select?: boolean;
  }) => void;
  renderButton: (
    parent: HTMLElement,
    options: {
      theme?: 'outline' | 'filled_blue' | 'filled_black';
      size?: 'large' | 'medium' | 'small';
      text?: 'signin_with' | 'signup_with' | 'continue_with' | 'signin';
      shape?: 'rectangular' | 'pill' | 'circle' | 'square';
      width?: number;
      locale?: string;
    },
  ) => void;
}

interface GoogleWindow extends Window {
  google?: {
    accounts?: {
      id?: GoogleAccountsId;
    };
  };
}

let gsiLoadPromise: Promise<GoogleAccountsId> | null = null;

function loadGoogleGsi(): Promise<GoogleAccountsId> {
  const win = window as GoogleWindow;
  if (win.google?.accounts?.id) {
    return Promise.resolve(win.google.accounts.id);
  }
  if (gsiLoadPromise) {
    return gsiLoadPromise;
  }

  gsiLoadPromise = new Promise<GoogleAccountsId>((resolve, reject) => {
    const resolveIfReady = () => {
      if (win.google?.accounts?.id) {
        resolve(win.google.accounts.id);
      } else {
        gsiLoadPromise = null;
        reject(new Error('Google Identity Services unavailable'));
      }
    };

    const existing = document.getElementById('google-gsi-client') as HTMLScriptElement | null;
    if (existing) {
      existing.addEventListener('load', resolveIfReady, { once: true });
      existing.addEventListener(
        'error',
        () => {
          gsiLoadPromise = null;
          reject(new Error('Failed to load Google Identity Services'));
        },
        { once: true },
      );
      return;
    }

    const script = document.createElement('script');
    script.id = 'google-gsi-client';
    script.src = GOOGLE_GSI_SRC;
    script.async = true;
    script.defer = true;
    script.addEventListener('load', resolveIfReady, { once: true });
    script.addEventListener(
      'error',
      () => {
        gsiLoadPromise = null;
        reject(new Error('Failed to load Google Identity Services'));
      },
      { once: true },
    );
    document.head.appendChild(script);
  });

  return gsiLoadPromise;
}

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  initialMode?: 'signin' | 'signup';
}

export const AuthModal: React.FC<AuthModalProps> = ({
  isOpen,
  onClose,
  initialMode = 'signin',
}) => {
  const [mode, setMode] = useState<'signin' | 'signup'>(initialMode);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [googleReady, setGoogleReady] = useState(false);
  const [googleFailed, setGoogleFailed] = useState(false);

  const googleButtonRef = useRef<HTMLDivElement | null>(null);
  const { signin, signup, googleLogin } = useAuth();

  const googleLoginRef = useRef(googleLogin);
  const onCloseRef = useRef(onClose);

  useEffect(() => {
    googleLoginRef.current = googleLogin;
    onCloseRef.current = onClose;
  }, [googleLogin, onClose]);

  useEffect(() => {
    if (isOpen) {
      setMode(initialMode);
      setError(null);
    }
  }, [isOpen, initialMode]);

  useEffect(() => {
    if (!isOpen || !GOOGLE_CLIENT_ID) {
      return;
    }

    let cancelled = false;

    loadGoogleGsi()
      .then((gsi) => {
        if (cancelled || !googleButtonRef.current) {
          return;
        }
        setGoogleFailed(false);
        gsi.initialize({
          client_id: GOOGLE_CLIENT_ID,
          callback: async (response) => {
            if (!response.credential) {
              setError('Не вдалося отримати дані облікового запису Google');
              return;
            }
            try {
              setError(null);
              setLoading(true);
              await googleLoginRef.current(response.credential);
              onCloseRef.current();
            } catch (err: unknown) {
              if (err instanceof Error) {
                setError(err.message);
              } else {
                setError('Не вдалося увійти через Google');
              }
            } finally {
              setLoading(false);
            }
          },
        });

        const container = googleButtonRef.current;
        container.innerHTML = '';
        const buttonWidth = Math.min(360, Math.max(220, container.offsetWidth || 320));
        gsi.renderButton(container, {
          theme: 'outline',
          size: 'large',
          text: mode === 'signin' ? 'signin_with' : 'signup_with',
          shape: 'rectangular',
          width: buttonWidth,
          locale: 'uk',
        });
        setGoogleReady(true);
      })
      .catch(() => {
        if (!cancelled) {
          setGoogleFailed(true);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [isOpen, mode]);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!email || !password) {
      setError('Будь ласка, заповніть усі обов’язкові поля');
      return;
    }

    if (password.length < 8) {
      setError('Пароль повинен містити не менше 8 символів');
      return;
    }

    try {
      setLoading(true);
      if (mode === 'signup') {
        await signup(email, password, name || undefined);
      } else {
        await signin(email, password);
      }
      onClose();
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('Не вдалося виконати операцію');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full overflow-hidden border border-slate-100">
        {/* Header Tabs */}
        <div className="flex border-b border-slate-100 bg-slate-50/70 relative">
          <button
            type="button"
            onClick={() => {
              setMode('signin');
              setError(null);
            }}
            className={`flex-1 py-4 text-center font-semibold text-sm transition-colors relative ${
              mode === 'signin'
                ? 'text-blue-600 bg-white'
                : 'text-slate-500 hover:text-slate-900'
            }`}
          >
            Вхід в акаунт
            {mode === 'signin' && (
              <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-blue-600" />
            )}
          </button>
          <button
            type="button"
            onClick={() => {
              setMode('signup');
              setError(null);
            }}
            className={`flex-1 py-4 text-center font-semibold text-sm transition-colors relative ${
              mode === 'signup'
                ? 'text-blue-600 bg-white'
                : 'text-slate-500 hover:text-slate-900'
            }`}
          >
            Реєстрація
            {mode === 'signup' && (
              <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-blue-600" />
            )}
          </button>
          <button
            onClick={onClose}
            className="absolute top-3.5 right-3.5 text-slate-400 hover:text-slate-600 p-1 rounded-full hover:bg-slate-200/50 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div className="text-center mb-2">
            <h3 className="text-lg font-bold text-slate-900">
              {mode === 'signin' ? 'З поверненням!' : 'Створити обліковий запис'}
            </h3>
            <p className="text-xs text-slate-500 mt-0.5">
              {mode === 'signin'
                ? 'Увійдіть, щоб переглядати та зберігати історію розрахунків'
                : 'Зберігайте свої розрахунки мита та порівнюйте сценарії'}
            </p>
          </div>

          {error && (
            <div className="flex items-start gap-2.5 p-3 rounded-xl bg-red-50 text-red-700 text-xs border border-red-200/80">
              <AlertCircle className="w-4 h-4 shrink-0 mt-0.5 text-red-500" />
              <span>{error}</span>
            </div>
          )}

          {GOOGLE_CLIENT_ID && !googleFailed && (
            <div className="space-y-3">
              <div className="flex flex-col items-center justify-center min-h-[44px]">
                {!googleReady && (
                  <div className="w-full h-[40px] rounded-lg border border-slate-200 bg-slate-50 flex items-center justify-center gap-2 text-xs font-medium text-slate-500">
                    <Loader2 className="w-3.5 h-3.5 animate-spin" />
                    <span>Увійти через Google...</span>
                  </div>
                )}
                <div
                  ref={googleButtonRef}
                  aria-label="Увійти через Google"
                  className="w-full flex justify-center"
                />
              </div>

              <div className="relative flex items-center">
                <div className="flex-grow border-t border-slate-200" />
                <span className="shrink-0 mx-3 text-[11px] font-medium uppercase tracking-wider text-slate-400">
                  або
                </span>
                <div className="flex-grow border-t border-slate-200" />
              </div>
            </div>
          )}

          {mode === 'signup' && (
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Ваше ім'я (необов'язково)
              </label>
              <div className="relative">
                <UserIcon className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Анна"
                  className="w-full pl-9 pr-3 py-2 text-sm border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/30 focus:border-blue-500"
                />
              </div>
            </div>
          )}

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Електронна пошта *
            </label>
            <div className="relative">
              <Mail className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="name@example.com"
                className="w-full pl-9 pr-3 py-2 text-sm border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/30 focus:border-blue-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Пароль (від 8 символів) *
            </label>
            <div className="relative">
              <Lock className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
              <input
                type="password"
                required
                minLength={8}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full pl-9 pr-3 py-2 text-sm border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/30 focus:border-blue-500"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full mt-2 py-2.5 px-4 bg-blue-600 hover:bg-blue-700 active:bg-blue-800 text-white font-semibold text-sm rounded-xl shadow-md shadow-blue-500/20 transition-all flex items-center justify-center gap-2 disabled:opacity-70"
          >
            {loading && <Loader2 className="w-4 h-4 animate-spin" />}
            {mode === 'signin' ? 'Увійти' : 'Зареєструватися'}
          </button>

          <p className="text-center text-xs text-slate-500 pt-2">
            {mode === 'signin' ? (
              <>
                Ще не маєте акаунту?{' '}
                <button
                  type="button"
                  onClick={() => {
                    setMode('signup');
                    setError(null);
                  }}
                  className="font-semibold text-blue-600 hover:underline"
                >
                  Зареєструватися
                </button>
              </>
            ) : (
              <>
                Вже зареєстровані?{' '}
                <button
                  type="button"
                  onClick={() => {
                    setMode('signin');
                    setError(null);
                  }}
                  className="font-semibold text-blue-600 hover:underline"
                >
                  Увійти
                </button>
              </>
            )}
          </p>
        </form>
      </div>
    </div>
  );
};
