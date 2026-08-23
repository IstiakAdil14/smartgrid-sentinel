'use client';

import { Activity } from 'lucide-react';

interface EvidenceGridProps {
  evidence: {
    transformer_load: number;
    electricity_demand: number;
    renewable_generation: number;
    temperature: number;
    rainfall: number;
    wind_speed: number;
  };
}

export function EvidenceGrid({ evidence }: EvidenceGridProps) {
  return (
    <div className="glass-panel p-5 h-full relative overflow-hidden group border border-slate-600/30">
      <div className="flex items-center mb-4 border-b border-slate-600/50 pb-3">
        <Activity className="text-emerald-400 w-5 h-5 mr-2" />
        <h2 className="text-lg font-medium text-slate-200 tracking-wide uppercase">Latest Telemetry Evidence</h2>
      </div>

      <div className="relative z-10">
        <table className="w-full text-sm text-left text-slate-300">
          <thead className="text-xs text-slate-400 uppercase bg-slate-800/50">
            <tr>
              <th scope="col" className="px-4 py-2 font-medium">Indicator</th>
              <th scope="col" className="px-4 py-2 font-medium text-right">Value</th>
            </tr>
          </thead>
          <tbody>
            <tr className="border-b border-slate-700/50 hover:bg-slate-700/20 transition-colors">
              <td className="px-4 py-2.5 font-medium">Transformer Load</td>
              <td className="px-4 py-2.5 text-right font-mono text-emerald-300">{evidence.transformer_load.toFixed(1)}%</td>
            </tr>
            <tr className="border-b border-slate-700/50 hover:bg-slate-700/20 transition-colors">
              <td className="px-4 py-2.5 font-medium">Electricity Demand</td>
              <td className="px-4 py-2.5 text-right font-mono text-amber-300">{evidence.electricity_demand.toFixed(1)} MW</td>
            </tr>
            <tr className="border-b border-slate-700/50 hover:bg-slate-700/20 transition-colors">
              <td className="px-4 py-2.5 font-medium">Renewable Gen.</td>
              <td className="px-4 py-2.5 text-right font-mono text-emerald-400">{evidence.renewable_generation.toFixed(1)} MW</td>
            </tr>
            <tr className="border-b border-slate-700/50 hover:bg-slate-700/20 transition-colors">
              <td className="px-4 py-2.5 font-medium">Temperature</td>
              <td className="px-4 py-2.5 text-right font-mono text-rose-300">{evidence.temperature.toFixed(1)} °C</td>
            </tr>
            <tr className="border-b border-slate-700/50 hover:bg-slate-700/20 transition-colors">
              <td className="px-4 py-2.5 font-medium">Rainfall</td>
              <td className="px-4 py-2.5 text-right font-mono text-blue-300">{evidence.rainfall.toFixed(1)} mm</td>
            </tr>
            <tr className="hover:bg-slate-700/20 transition-colors">
              <td className="px-4 py-2.5 font-medium">Wind Speed</td>
              <td className="px-4 py-2.5 text-right font-mono text-sky-300">{evidence.wind_speed.toFixed(1)} m/s</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}
