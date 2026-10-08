import React from 'react';
import { useTranslation } from 'react-i18next';
import { Stethoscope, AlertTriangle } from 'lucide-react';

export const Footer: React.FC = () => {
  const { t } = useTranslation();

  return (
    <footer className="bg-white border-t border-surface-border pt-16 pb-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto space-y-10">
        {/* Clinical Safety Disclaimer Banner */}
        <div className="bg-surface-alt border border-surface-border rounded-card p-4 sm:p-5 flex items-start gap-3.5 text-slate-dark">
          <AlertTriangle className="w-5 h-5 text-amber-500 flex-shrink-0 mt-0.5" />
          <p className="text-xs sm:text-sm font-medium leading-relaxed">
            <span className="font-bold text-navy">Clinical Safety Disclaimer: </span>
            {t('footer.disclaimer')}
          </p>
        </div>

        <div className="flex flex-col md:flex-row items-center justify-between gap-6 pt-6 border-t border-surface-border">
          <div className="flex items-center gap-2.5 text-navy font-bold text-lg">
            <div className="w-8 h-8 rounded-lg bg-navy flex items-center justify-center text-teal-100">
              <Stethoscope className="w-4 h-4" />
            </div>
            <span>ScribeCare</span>
            <span className="text-xs text-slate font-normal ml-2">
              © {new Date().getFullYear()} {t('footer.rights')}
            </span>
          </div>

          <div className="flex flex-wrap items-center gap-6 text-sm text-slate">
            <a href="#privacy" className="hover:text-navy transition-colors">{t('footer.privacy')}</a>
            <a href="#terms" className="hover:text-navy transition-colors">{t('footer.terms')}</a>
            <a href="#compliance" className="hover:text-navy transition-colors">{t('footer.compliance')}</a>
          </div>
        </div>
      </div>
    </footer>
  );
};
