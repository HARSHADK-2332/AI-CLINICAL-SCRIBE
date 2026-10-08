import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Stethoscope, Menu, X, Globe, Sparkles } from 'lucide-react';

interface NavbarProps {
  onOpenDemo: () => void;
  currentPath: string;
  onNavigate: (path: string) => void;
}

export const Navbar: React.FC<NavbarProps> = ({ onOpenDemo, currentPath, onNavigate }) => {
  const { t, i18n } = useTranslation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const languages = [
    { code: 'en', label: 'English' },
    { code: 'hi', label: 'हिंदी' },
    { code: 'te', label: 'తెలుగు' }
  ];

  const handleLangChange = (code: string) => {
    i18n.changeLanguage(code);
  };

  return (
    <header className="sticky top-0 z-40 bg-white/90 backdrop-blur-md border-b border-surface-border">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between">
        {/* Wordmark */}
        <button
          onClick={() => onNavigate('/')}
          className="flex items-center gap-2.5 text-navy font-extrabold text-2xl tracking-tight hover:opacity-90 transition-opacity"
          aria-label="ScribeCare Home"
        >
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-navy to-teal flex items-center justify-center text-white shadow-soft">
            <Stethoscope className="w-5 h-5 text-teal-100" />
          </div>
          <span>ScribeCare</span>
          <span className="hidden sm:inline-block text-[11px] font-semibold tracking-wider text-teal bg-teal-100 px-2 py-0.5 rounded-full uppercase">
            Ambient AI
          </span>
        </button>

        {/* Desktop Nav Links */}
        <nav className="hidden md:flex items-center gap-8 text-[15px] font-medium text-slate">
          <a href="#product" className="hover:text-navy transition-colors">{t('nav.product')}</a>
          <a href="#solutions" className="hover:text-navy transition-colors">{t('nav.solutions')}</a>
          <a href="#security" className="hover:text-navy transition-colors">{t('nav.security')}</a>
          <a href="#resources" className="hover:text-navy transition-colors">{t('nav.resources')}</a>
        </nav>

        {/* Right CTA Actions */}
        <div className="hidden md:flex items-center gap-4">
          {/* Language Selector Dropdown */}
          <div className="flex items-center bg-surface-alt border border-surface-border rounded-pill p-1">
            <Globe className="w-3.5 h-3.5 text-slate ml-2 mr-1" />
            {languages.map((l) => (
              <button
                key={l.code}
                onClick={() => handleLangChange(l.code)}
                className={`text-xs px-2.5 py-1 rounded-pill font-medium transition-colors ${
                  i18n.language === l.code
                    ? 'bg-teal text-white shadow-sm'
                    : 'text-slate hover:text-navy'
                }`}
                aria-label={`Switch language to ${l.label}`}
              >
                {l.label}
              </button>
            ))}
          </div>

          {currentPath === '/' ? (
            <button
              onClick={() => onNavigate('/app')}
              className="text-sm font-semibold text-navy hover:text-teal transition-colors flex items-center gap-1.5 px-3 py-2"
            >
              <Sparkles className="w-4 h-4 text-teal" />
              {t('nav.openApp')}
            </button>
          ) : (
            <button
              onClick={() => onNavigate('/')}
              className="text-sm font-semibold text-slate hover:text-navy transition-colors px-3 py-2"
            >
              ← Landing
            </button>
          )}

          <button
            onClick={onOpenDemo}
            className="bg-navy hover:bg-navy-800 text-white text-sm font-semibold px-4 py-2.5 rounded-btn shadow-soft transition-all duration-200 active:scale-95"
          >
            {t('nav.requestDemo')}
          </button>
        </div>

        {/* Mobile Menu Button */}
        <button
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          className="md:hidden p-2 rounded-btn text-slate hover:text-navy hover:bg-surface-alt transition-colors"
          aria-label="Toggle navigation menu"
          aria-expanded={mobileMenuOpen}
        >
          {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
        </button>
      </div>

      {/* Mobile Drawer */}
      {mobileMenuOpen && (
        <div className="md:hidden border-b border-surface-border bg-white px-4 pt-3 pb-6 space-y-4">
          <nav className="flex flex-col space-y-3 font-medium text-slate">
            <a href="#product" onClick={() => setMobileMenuOpen(false)} className="px-2 py-1.5 hover:text-navy">{t('nav.product')}</a>
            <a href="#solutions" onClick={() => setMobileMenuOpen(false)} className="px-2 py-1.5 hover:text-navy">{t('nav.solutions')}</a>
            <a href="#security" onClick={() => setMobileMenuOpen(false)} className="px-2 py-1.5 hover:text-navy">{t('nav.security')}</a>
            <a href="#resources" onClick={() => setMobileMenuOpen(false)} className="px-2 py-1.5 hover:text-navy">{t('nav.resources')}</a>
          </nav>

          <div className="pt-2 border-t border-surface-border flex flex-col gap-3">
            <div className="flex items-center gap-2">
              <span className="text-xs text-slate font-medium">Language:</span>
              {languages.map((l) => (
                <button
                  key={l.code}
                  onClick={() => handleLangChange(l.code)}
                  className={`text-xs px-2.5 py-1 rounded-pill ${
                    i18n.language === l.code ? 'bg-teal text-white' : 'bg-surface-alt text-slate'
                  }`}
                >
                  {l.label}
                </button>
              ))}
            </div>

            <button
              onClick={() => { setMobileMenuOpen(false); onNavigate('/app'); }}
              className="w-full bg-teal-100 text-teal-700 font-semibold text-sm py-2.5 rounded-btn flex items-center justify-center gap-2"
            >
              <Sparkles className="w-4 h-4" />
              {t('nav.openApp')}
            </button>

            <button
              onClick={() => { setMobileMenuOpen(false); onOpenDemo(); }}
              className="w-full bg-navy text-white font-semibold text-sm py-2.5 rounded-btn"
            >
              {t('nav.requestDemo')}
            </button>
          </div>
        </div>
      )}
    </header>
  );
};
