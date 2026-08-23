'use client';

import { FileText } from 'lucide-react';

interface ExplanationCardProps {
  explanation: string;
}

export function ExplanationCard({ explanation }: ExplanationCardProps) {
  return (
    <div className="glass-panel p-5 h-full relative overflow-hidden group border border-slate-600/30 shadow-[0_0_15px_rgba(59,130,246,0.05)]">
      <div className="absolute -right-10 -top-10 w-32 h-32 bg-blue-500/5 rounded-full blur-3xl group-hover:bg-blue-400/10 transition-all duration-700"></div>
      
      <div className="flex items-center mb-4 border-b border-slate-600/50 pb-3">
        <FileText className="text-blue-400 w-5 h-5 mr-2" />
        <h2 className="text-lg font-medium text-slate-200 tracking-wide uppercase">Why this risk?</h2>
      </div>

      <div className="relative z-10 text-slate-300 font-light leading-relaxed">
        {explanation}
      </div>
    </div>
  );
}
