import React from 'react';
import type { LLMExplanation } from '../types/api';
import { AlertCircle, FileText, CheckCircle2, ChevronRight, HelpCircle } from 'lucide-react';


interface Props {
  explanation: LLMExplanation;
  workflow?: string;
}

const ExplanationCard: React.FC<Props> = ({ explanation, workflow }) => {
  const isFallback = explanation.what_results_suggest?.includes("unavailable") || explanation.what_results_suggest?.includes("Fallback");
  const headingTitle = workflow === "CLINICAL_REPORT" ? "Clinical Report Synthesis" : "Questionnaire Screening Overview";

  return (
    <div className="bg-white rounded-3xl border border-slate-200 overflow-hidden mb-8 shadow-xs">
      <div className="bg-slate-50 px-6 py-5 border-b border-slate-200 flex items-center justify-between">
        <h2 className="text-xl font-extrabold text-slate-900 flex items-center">
          <FileText className="w-6 h-6 mr-3 text-blue-600" />
          LLM Clinical Synthesis & Executive Summary
        </h2>
        {isFallback && (
          <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-amber-50 border border-amber-200 text-amber-800">
            Fallback Mode
          </span>
        )}
      </div>
      
      <div className="p-6 sm:p-8 space-y-8">
        {/* Result Heading */}
        <div>
          <h3 className="text-xs font-bold uppercase tracking-wider text-blue-700 flex items-center mb-3">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 mr-2" />
            {headingTitle}
          </h3>
          <p className="text-slate-900 leading-relaxed text-base sm:text-lg bg-blue-50/60 p-5 rounded-2xl border border-blue-100 font-medium">
            {explanation.what_results_suggest}
          </p>
        </div>
        
        {/* What this may mean */}
        <div>
          <h3 className="text-xs font-bold uppercase tracking-wider text-indigo-700 flex items-center mb-3">
            <HelpCircle className="w-4 h-4 text-indigo-600 mr-2" />
            Clinical Interpretation & Relevance
          </h3>
          <p className="text-slate-700 leading-relaxed text-sm sm:text-base">
            {explanation.why_relevant}
          </p>
        </div>
        
        {/* What research says */}
        {explanation.what_research_says && explanation.what_research_says.length > 0 && (
          <div>
            <h3 className="text-xs font-bold uppercase tracking-wider text-teal-700 mb-3">Biomedical Research Evidence</h3>
            <div className="space-y-2.5">
              {explanation.what_research_says.map((ev: string, i: number) => (
                <div key={i} className="flex items-start bg-slate-50 p-4 rounded-xl border border-slate-200">
                  <ChevronRight className="w-4 h-4 text-teal-600 mt-0.5 mr-2 flex-shrink-0" />
                  <span className="text-slate-700 text-sm leading-relaxed">{ev}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Next Steps */}
        {explanation.next_steps && explanation.next_steps.length > 0 && (
          <div>
            <h3 className="text-xs font-bold uppercase tracking-wider text-emerald-700 mb-3">Recommended Next Steps</h3>
            <div className="bg-emerald-50/60 rounded-2xl p-5 border border-emerald-100">
              <ul className="space-y-3">
                {explanation.next_steps.map((step: string, i: number) => (
                  <li key={i} className="flex items-start">
                    <div className="w-6 h-6 rounded-full bg-emerald-100 border border-emerald-200 text-emerald-800 flex items-center justify-center text-xs font-bold mt-0.5 mr-3 flex-shrink-0">
                      {i + 1}
                    </div>
                    <span className="text-slate-800 text-sm leading-relaxed">{step}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}
        
        {/* Clinical Notice */}
        <div className="bg-amber-50 rounded-2xl p-5 border border-amber-200">
          <div className="flex items-start space-x-3">
            <AlertCircle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
            <div>
              <h4 className="text-xs font-bold uppercase tracking-wider text-amber-900 mb-1">Mandatory Clinical Disclaimer</h4>
              <p className="text-amber-800/90 text-xs leading-relaxed">
                {explanation.clinical_notice || "This screening is for research-oriented health assessment and does not diagnose Alzheimer's disease or Parkinson's disease or determine disease stage. Please consult a qualified healthcare professional for clinical evaluation."}
              </p>
            </div>
          </div>
        </div>
        
      </div>
    </div>
  );
};

export default ExplanationCard;

