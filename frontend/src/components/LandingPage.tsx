import React from 'react';
import { useTranslation } from 'react-i18next';
import { Globe, Play, Sparkles } from 'lucide-react';
import { TrustStrip } from './TrustStrip';
import { FeatureGrid } from './FeatureGrid';
import { LaptopMockup } from './LaptopMockup';

interface LandingPageProps {
  onOpenDemo: () => void;
  onNavigateApp: () => void;
}

export const LandingPage: React.FC<LandingPageProps> = ({ onOpenDemo, onNavigateApp }) => {
  const { t, i18n } = useTranslation();

  const languages = [
    { code: 'en', label: 'English' },
    { code: 'hi', label: 'हिंदी' },
    { code: 'te', label: 'తెలుగు' }
  ];

  const handleLanguageSwitch = (code: string) => {
    i18n.changeLanguage(code);
  };

  const scrollToDemo = () => {
    const el = document.getElementById('interactive-demo');
    if (el) {
      el.scrollIntoView({ behavior: 'smooth' });
    } else {
      onNavigateApp();
    }
  };

  return (
    <div className="flex flex-col min-h-screen">
      {/* Hero Section */}
      <section className="relative pt-12 pb-20 lg:pt-20 lg:pb-32 overflow-hidden bg-gradient-to-b from-white via-surface-alt/40 to-white">
        {/* Subtle grid background */}
        <div className="absolute inset-0 bg-grid-pattern opacity-60 pointer-events-none" />

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-8 items-center">
            {/* Left Hero Column */}
            <div className="lg:col-span-6 space-y-8 text-center lg:text-left z-10">
              {/* Eyebrow */}
              <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-teal-100/90 border border-teal-200">
                <Sparkles className="w-3.5 h-3.5 text-teal" />
                <span className="text-xs font-bold uppercase tracking-widest text-teal">
                  {t('hero.eyebrow')}
                </span>
              </div>

              {/* H1 Heading */}
              <h1 className="text-4xl sm:text-5xl lg:text-[58px] font-extrabold text-navy tracking-tight leading-[1.12]">
                <span className="block">{t('hero.titleLine1')}</span>
                <span className="block text-navy/90">{t('hero.titleLine2')}</span>
              </h1>

              {/* Subcopy */}
              <p className="text-base sm:text-lg text-slate max-w-xl mx-auto lg:mx-0 leading-relaxed">
                {t('hero.subtitle')}
              </p>

              {/* Dual CTAs */}
              <div className="flex flex-col sm:flex-row items-center justify-center lg:justify-start gap-4 pt-2">
                <button
                  onClick={onOpenDemo}
                  className="w-full sm:w-auto bg-navy hover:bg-navy-800 text-white font-bold text-base px-7 py-3.5 rounded-btn shadow-card flex items-center justify-center gap-2.5 transition-all duration-200 hover:-translate-y-0.5 active:translate-y-0"
                >
                  <span>{t('hero.requestDemoCta')}</span>
                </button>

                <button
                  onClick={scrollToDemo}
                  className="w-full sm:w-auto bg-white hover:bg-surface-alt text-navy font-semibold text-base px-6 py-3.5 rounded-btn border border-surface-border shadow-soft flex items-center justify-center gap-2 transition-all hover:border-slate-subtle"
                >
                  <Play className="w-4 h-4 fill-navy text-navy" />
                  <span>{t('hero.seeHowItWorks')}</span>
                </button>
              </div>

              {/* Language Pills Selector */}
              <div className="pt-4 flex flex-wrap items-center justify-center lg:justify-start gap-2.5">
                <div className="flex items-center gap-1.5 text-xs text-slate font-medium mr-1">
                  <Globe className="w-3.5 h-3.5 text-teal" />
                  <span>{t('hero.availableIn')}:</span>
                </div>

                {languages.map((l) => (
                  <button
                    key={l.code}
                    onClick={() => handleLanguageSwitch(l.code)}
                    className={`text-xs font-bold px-3 py-1.5 rounded-pill border transition-all ${
                      i18n.language === l.code
                        ? 'bg-teal-100 text-teal-800 border-teal-300 shadow-sm ring-1 ring-teal-300'
                        : 'bg-white text-slate hover:text-navy border-surface-border hover:bg-surface-alt'
                    }`}
                  >
                    {l.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Right Hero Column: Laptop Mockup */}
            <div className="lg:col-span-6 flex justify-center lg:justify-end" id="interactive-demo">
              <LaptopMockup />
            </div>
          </div>
        </div>
      </section>

      {/* Trust Strip */}
      <TrustStrip />

      {/* Feature Cards Grid */}
      <FeatureGrid onLearnMore={() => onOpenDemo()} />
    </div>
  );
};
