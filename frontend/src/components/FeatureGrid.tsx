import React from 'react';
import { useTranslation } from 'react-i18next';
import { Mic, FileCheck, LockKeyhole } from 'lucide-react';

interface FeatureGridProps {
  onLearnMore: (feature: string) => void;
}

export const FeatureGrid: React.FC<FeatureGridProps> = ({ onLearnMore }) => {
  const { t } = useTranslation();

  const features = [
    {
      id: 'ambient',
      icon: Mic,
      title: t('features.feature1Title'),
      desc: t('features.feature1Desc'),
    },
    {
      id: 'structured',
      icon: FileCheck,
      title: t('features.feature2Title'),
      desc: t('features.feature2Desc'),
    },
    {
      id: 'security',
      icon: LockKeyhole,
      title: t('features.feature3Title'),
      desc: t('features.feature3Desc'),
    },
  ];

  return (
    <section id="features" className="py-24 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
      <div className="text-center max-w-3xl mx-auto mb-16">
        <span className="text-xs font-bold uppercase tracking-widest text-teal bg-teal-100 px-3 py-1 rounded-full">
          Capabilities
        </span>
        <h2 className="mt-4 text-3xl sm:text-4xl font-extrabold text-navy tracking-tight">
          Purpose-built for clinical encounters
        </h2>
        <p className="mt-4 text-lg text-slate">
          Reclaim hours spent on electronic health records with an ambient documentation partner that works the way clinicians think.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {features.map((feature) => {
          const Icon = feature.icon;
          return (
            <div
              key={feature.id}
              className="group relative bg-white border border-surface-border rounded-card p-8 shadow-soft hover:shadow-card hover:border-teal-200 transition-all duration-300 flex flex-col justify-between"
            >
              <div>
                {/* Circular light-teal icon badge */}
                <div className="w-14 h-14 rounded-full bg-teal-100 flex items-center justify-center text-teal-600 mb-6 group-hover:bg-teal group-hover:text-white transition-colors duration-300">
                  <Icon className="w-7 h-7" />
                </div>
                <h3 className="text-xl font-bold text-navy mb-3">
                  {feature.title}
                </h3>
                <p className="text-slate leading-relaxed text-[15px]">
                  {feature.desc}
                </p>
              </div>

              <div className="mt-8 pt-4 border-t border-surface-border/60">
                <button
                  onClick={() => onLearnMore(feature.id)}
                  className="text-sm font-semibold text-teal hover:text-teal-700 flex items-center gap-1.5 group-hover:gap-2.5 transition-all"
                >
                  <span>{t('features.learnMore')}</span>
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
};
