import React from 'react';
import { AppScreen } from './AppScreen';

interface LaptopMockupProps {
  onInteract?: () => void;
}

export const LaptopMockup: React.FC<LaptopMockupProps> = () => {
  return (
    <div className="relative w-full max-w-[800px] mx-auto lg:max-w-none lg:w-[120%] lg:-mr-24 select-none">
      {/* Ambient glow behind laptop */}
      <div className="absolute -inset-4 bg-gradient-to-r from-teal-200/40 to-navy-200/30 blur-2xl -z-10 rounded-full" />

      {/* Laptop Screen Bezel */}
      <div className="relative bg-[#0F172A] rounded-t-[20px] p-2.5 sm:p-3.5 shadow-laptop border border-slate-700/60">
        {/* Top Camera and Sensor */}
        <div className="flex items-center justify-center gap-1.5 pb-2">
          <span className="w-1.5 h-1.5 rounded-full bg-slate-700" />
          <span className="w-2 h-2 rounded-full bg-slate-900 border border-slate-700 flex items-center justify-center">
            <span className="w-1 h-1 rounded-full bg-teal-500/80" />
          </span>
        </div>

        {/* Laptop Screen Content (Interactive App Preview) */}
        <div className="relative bg-white rounded-lg overflow-hidden border border-slate-800 shadow-inner h-[480px] sm:h-[540px] md:h-[580px] overflow-y-auto">
          <AppScreen embedded={true} />
        </div>
      </div>

      {/* Laptop Bottom Aluminum Base */}
      <div className="relative bg-gradient-to-b from-[#CBD5E1] to-[#94A3B8] h-4 rounded-b-xl shadow-md border-t border-slate-300">
        {/* Trackpad notch */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-24 h-1.5 bg-slate-400 rounded-b-md" />
      </div>
      {/* Bottom chassis foot shadow */}
      <div className="mx-auto w-[92%] h-2 bg-gradient-to-b from-slate-400/40 to-transparent blur-sm rounded-full" />
    </div>
  );
};
