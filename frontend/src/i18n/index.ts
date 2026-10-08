import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import en from './locales/en.json';
import hi from './locales/hi.json';
import te from './locales/te.json';

const savedLang = (typeof window !== 'undefined' && localStorage.getItem('scribecare_lang')) || 'en';

i18n
  .use(initReactI18next)
  .init({
    resources: {
      en: { translation: en },
      hi: { translation: hi },
      te: { translation: te },
    },
    lng: savedLang,
    fallbackLng: 'en',
    interpolation: {
      escapeValue: false,
    },
  });

// Update html lang attribute on initialize and change
if (typeof document !== 'undefined') {
  document.documentElement.lang = savedLang;
}

i18n.on('languageChanged', (lng) => {
  if (typeof window !== 'undefined') {
    localStorage.setItem('scribecare_lang', lng);
    document.documentElement.lang = lng;
  }
});

export default i18n;
