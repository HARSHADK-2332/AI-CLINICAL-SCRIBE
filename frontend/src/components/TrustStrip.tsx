import React from 'react';
import { useTranslation } from 'react-i18next';
import { ShieldCheck, Users, FileText, Globe } from 'lucide-react';

export const TrustStrip: React.FC = () => {
  const { t } = useTranslation();

  const items = [
    {
      icon: ShieldCheck,
      title: t('trust.item1Title'),
      desc: t('trust.item1Desc'),
    },
    {
      icon: Users,
      title: t('trust.item2Title'),
      desc: t('trust.item2Desc'),
    },
    {
      icon: FileText,
      title: t('trust.item3Title'),
      desc: t('trust.item3Desc'),
    },
    {
      icon: Globe,
      title: t('trust.item4Title'),
      desc: t('trust.item4Desc'),
    },
  ];

  return (
    <section className="bg-surface-alt border-y border-surface-border py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8 text-center lg:text-left">
          <p className="text-xs font-bold tracking-widest text-teal uppercase">
            {t('trust.heading')}
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8 lg:gap-0 lg:divide-x lg:divide-surface-border">
          {items.map((item, idx) => {
            const Icon = item.icon;
            return (
              <div
                key={idx}
                className="flex items-start gap-4 lg:px-6 first:lg:pl-0 last:lg:pr-0"
              >
                <div className="flex-shrink-0 w-11 h-11 rounded-card bg-teal-100 flex items-center justify-center text-teal-600 border border-teal-200">
                  <Icon className="w-5 h-5 stroke-[1.8]" />
                </div>
                <div>
                  <h4 className="text-[15px] font-bold text-navy tracking-tight">
                    {item.title}
                  </h4>
                  <p className="mt-1 text-sm text-slate leading-relaxed">
                    {item.desc}
                  </p>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
};
