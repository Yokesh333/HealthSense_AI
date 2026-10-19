import React from 'react';
import { Brain, Activity, Layers, ArrowLeft } from 'lucide-react';

export type ScreeningType = "alzheimers" | "parkinsons" | "both";

interface ScreeningTypeSelectorProps {
  onSelect: (type: ScreeningType) => void;
  onBack: () => void;
}

export const ScreeningTypeSelector: React.FC<ScreeningTypeSelectorProps> = ({ onSelect, onBack }) => {
  return (
    <div className="max-w-4xl mx-auto py-10 px-4 sm:px-6 lg:px-8">
      <button 
        onClick={onBack}
        className="mb-8 inline-flex items-center text-slate-600 hover:text-slate-900 transition-colors text-sm font-medium bg-white border border-slate-200 px-4 py-2 rounded-xl shadow-xs cursor-pointer"
      >
        <ArrowLeft className="w-4 h-4 mr-2" />
        Back to Home
      </button>

      <div className="text-center mb-12 space-y-3">
        <h2 className="text-3xl font-extrabold text-slate-900 sm:text-4xl tracking-tight">
          Select Clinical Screening Domain
        </h2>
        <p className="text-slate-600 max-w-xl mx-auto text-base">
          Choose the neurological domain you want to evaluate. You can screen cognitive changes, motor/movement symptoms, or run a combined evaluation.
        </p>
      </div>

      <div className="grid md:grid-cols-3 gap-6 max-w-4xl mx-auto">
        {/* Memory & Thinking (Alzheimer's) */}
        <button
          onClick={() => onSelect("alzheimers")}
          className="group relative bg-white border border-slate-200 rounded-3xl p-6 text-left flex flex-col h-full hover:border-purple-500 hover:shadow-md transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-purple-500 cursor-pointer shadow-xs"
        >
          <div className="flex items-center justify-between mb-4">
            <div className="bg-purple-50 border border-purple-200 w-12 h-12 rounded-2xl flex items-center justify-center group-hover:bg-purple-600 transition-colors duration-300">
              <Brain className="w-6 h-6 text-purple-600 group-hover:text-white transition-colors" />
            </div>
            <span className="text-[11px] font-bold uppercase tracking-wider text-purple-700 bg-purple-50 border border-purple-200 px-2.5 py-0.5 rounded-full">
              ADNI Protocol
            </span>
          </div>

          <h3 className="text-xl font-bold text-slate-900 mb-2 group-hover:text-purple-600 transition-colors">
            Memory & Thinking
          </h3>
          <p className="text-sm text-slate-600 flex-grow leading-relaxed mb-6">
            Evaluates cognitive function, memory recall, orientation, language, and everyday executive activities (Alzheimer’s profile).
          </p>

          <div className="w-full py-2.5 px-4 bg-purple-50 border border-purple-200 rounded-xl text-xs font-bold text-purple-700 text-center group-hover:bg-purple-600 group-hover:text-white transition-colors">
            Start Alzheimer's Screening →
          </div>
        </button>

        {/* Movement & Mobility (Parkinson's) */}
        <button
          onClick={() => onSelect("parkinsons")}
          className="group relative bg-white border border-slate-200 rounded-3xl p-6 text-left flex flex-col h-full hover:border-teal-500 hover:shadow-md transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-teal-500 cursor-pointer shadow-xs"
        >
          <div className="flex items-center justify-between mb-4">
            <div className="bg-teal-50 border border-teal-200 w-12 h-12 rounded-2xl flex items-center justify-center group-hover:bg-teal-600 transition-colors duration-300">
              <Activity className="w-6 h-6 text-teal-600 group-hover:text-white transition-colors" />
            </div>
            <span className="text-[11px] font-bold uppercase tracking-wider text-teal-700 bg-teal-50 border border-teal-200 px-2.5 py-0.5 rounded-full">
              PPMI Protocol
            </span>
          </div>

          <h3 className="text-xl font-bold text-slate-900 mb-2 group-hover:text-teal-600 transition-colors">
            Movement & Mobility
          </h3>
          <p className="text-sm text-slate-600 flex-grow leading-relaxed mb-6">
            Evaluates motor symptoms, gait, tremor, rigidity, sleep patterns, and non-motor indicators (Parkinson’s profile).
          </p>

          <div className="w-full py-2.5 px-4 bg-teal-50 border border-teal-200 rounded-xl text-xs font-bold text-teal-700 text-center group-hover:bg-teal-600 group-hover:text-white transition-colors">
            Start Parkinson's Screening →
          </div>
        </button>

        {/* Combined Dual Screening */}
        <button
          onClick={() => onSelect("both")}
          className="group relative bg-white border border-slate-200 rounded-3xl p-6 text-left flex flex-col h-full hover:border-blue-500 hover:shadow-md transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-blue-500 cursor-pointer shadow-xs"
        >
          <div className="flex items-center justify-between mb-4">
            <div className="bg-blue-50 border border-blue-200 w-12 h-12 rounded-2xl flex items-center justify-center group-hover:bg-blue-600 transition-colors duration-300">
              <Layers className="w-6 h-6 text-blue-600 group-hover:text-white transition-colors" />
            </div>
            <span className="text-[11px] font-bold uppercase tracking-wider text-blue-700 bg-blue-50 border border-blue-200 px-2.5 py-0.5 rounded-full">
              Full Multimodal
            </span>
          </div>

          <h3 className="text-xl font-bold text-slate-900 mb-2 group-hover:text-blue-600 transition-colors">
            Combined Evaluation
          </h3>
          <p className="text-sm text-slate-600 flex-grow leading-relaxed mb-6">
            Comprehensive dual screening covering both cognitive and motor symptoms for dual Random Forest model inference.
          </p>

          <div className="w-full py-2.5 px-4 bg-blue-50 border border-blue-200 rounded-xl text-xs font-bold text-blue-700 text-center group-hover:bg-blue-600 group-hover:text-white transition-colors">
            Start Full Evaluation →
          </div>
        </button>
      </div>
    </div>
  );
};

