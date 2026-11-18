import type React from 'react';
import { Beer, Wine, Martini, Cigarette, Flame, Leaf, Zap, Droplets, Fuel } from 'lucide-react';
import type { ExciseKindKey } from '../types/api';

// Presentation only; units, duty-free norms and required fields come from the backend (GET /api/excise/kinds).
export const KIND_UI: Record<ExciseKindKey, { icon: React.ElementType; short: string; quantity: string; price: string; unit: string }> = {
  beer: { icon: Beer, short: 'Пиво', quantity: '10', price: '20', unit: 'л' },
  wine: { icon: Wine, short: 'Вино', quantity: '3', price: '30', unit: 'л' },
  sparkling_wine: { icon: Wine, short: 'Ігристе вино', quantity: '3', price: '45', unit: 'л' },
  spirits: { icon: Martini, short: 'Міцний алкоголь', quantity: '2', price: '60', unit: 'л' },
  cigarettes: { icon: Cigarette, short: 'Сигарети', quantity: '400', price: '100', unit: 'шт' },
  cigars: { icon: Flame, short: 'Сигари', quantity: '60', price: '120', unit: 'шт' },
  smoking_tobacco: { icon: Leaf, short: 'Тютюн, кальян', quantity: '500', price: '40', unit: 'г' },
  heated_tobacco: { icon: Zap, short: 'Стіки IQOS / glo', quantity: '200', price: '40', unit: 'шт' },
  e_liquid: { icon: Droplets, short: 'Рідини для е-сигарет', quantity: '30', price: '15', unit: 'мл' },
  petrol: { icon: Fuel, short: 'Бензин', quantity: '40', price: '70', unit: 'л' },
  diesel: { icon: Fuel, short: 'Дизпальне', quantity: '40', price: '65', unit: 'л' },
};

