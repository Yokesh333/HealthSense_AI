import React from 'react';
import { ShieldCheck, RotateCcw, Activity } from 'lucide-react';
import type { AgentAnalysisResponse } from '../types/api';
import ExplanationCard from './ExplanationCard';
import { TechnicalAnalysis } from './TechnicalAnalysis';
import { FollowUpChat } from './FollowUpChat';

interface ScreeningResultProps {
  result: AgentAnalysisResponse;
  onReset: () => void;
}

export const ScreeningResult: React.FC<ScreeningResultProps> = ({ result, onReset }) => {
  return (
    <div className="max-w-5xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
      {/* Top Header Bar */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between mb-8 pb-6 border-b border-slate-200 gap-4">
        <div className="flex items-center space-x-4">
          <div className="bg-emerald-50 border border-emerald-200 p-3 rounded-2xl shadow-xs">
            <ShieldCheck className="w-8 h-8 text-emerald-600" />
          </div>
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-[11px] font-bold uppercase tracking-wider text-emerald-700 bg-emerald-50 border border-emerald-200 px-2.5 py-0.5 rounded-full inline-flex items-center gap-1">
                <Activity className="w-3 h-3 text-emerald-600" />
                Screening Completed
              </span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight">
              {result.workflow === "CLINICAL_REPORT" ? "Clinical Report Evaluation" : "Screening Profile Results"}
            </h1>
          </div>
        </div>
        
        <button
          onClick={onReset}
          className="flex items-center px-4 py-2.5 bg-white border border-slate-300 rounded-xl text-xs font-bold text-slate-700 hover:text-slate-900 hover:border-slate-400 transition-colors shadow-xs focus:outline-none focus:ring-2 focus:ring-blue-500 cursor-pointer"
        >
          <RotateCcw className="w-4 h-4 mr-2 text-slate-500" />
          Start New Assessment
        </button>
      </div>

      {/* Main Content Sections */}
      <div className="space-y-8">
        <ExplanationCard explanation={result.explanation} workflow={result.workflow} />
        
        <TechnicalAnalysis result={result} />
        
        <FollowUpChat initialResult={result} />
      </div>
    </div>
  );
};

