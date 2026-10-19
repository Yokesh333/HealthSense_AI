import React from 'react';
import { FileText, ClipboardList, Shield, Cpu, BookOpen, Activity } from 'lucide-react';

interface LandingPageProps {
  onSelectAction: (action: "report" | "questionnaire") => void;
}

export const LandingPage: React.FC<LandingPageProps> = ({ onSelectAction }) => {
  return (
    <div className="max-w-6xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
      {/* Hero Header */}
      <div className="text-center mb-14 space-y-4">
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-blue-50 border border-blue-200 text-blue-700 text-xs font-semibold uppercase tracking-wider shadow-xs">
          <Activity className="w-3.5 h-3.5 animate-pulse text-blue-600" />
          <span>Multimodal Clinical Intelligence Platform</span>
        </div>
        <h1 className="text-4xl font-black text-slate-900 sm:text-6xl tracking-tight leading-tight">
          HealthSense <span className="text-blue-600">AI</span>
        </h1>
        <p className="text-lg sm:text-xl text-slate-600 max-w-2xl mx-auto font-normal leading-relaxed">
          AI-Assisted Cognitive & Neurological Health Screening, Explainable Machine Learning & Biomedical Evidence Retrieval
        </p>
      </div>

      {/* Main Action Cards */}
      <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto mb-16">
        {/* Card 1: Upload Clinical Report */}
        <button
          onClick={() => onSelectAction("report")}
          className="group relative bg-white border border-slate-200 rounded-3xl p-8 text-left flex flex-col h-full hover:border-blue-500 hover:shadow-lg transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-blue-500 cursor-pointer shadow-xs"
        >
          <div className="flex items-center justify-between mb-6">
            <div className="bg-blue-50 border border-blue-200 w-14 h-14 rounded-2xl flex items-center justify-center group-hover:bg-blue-600 group-hover:border-blue-600 transition-colors duration-300">
              <FileText className="w-7 h-7 text-blue-600 group-hover:text-white transition-colors duration-300" />
            </div>
            <span className="text-xs font-semibold uppercase tracking-wider text-blue-700 bg-blue-50 border border-blue-200 px-3 py-1 rounded-full">
              Automated Extraction
            </span>
          </div>

          <h3 className="text-2xl font-extrabold text-slate-900 mb-3 group-hover:text-blue-600 transition-colors">
            Upload Clinical Report
          </h3>
          <p className="text-slate-600 flex-grow mb-8 text-sm sm:text-base leading-relaxed">
            Extract demographics, cognitive scores (MMSE, MoCA, CDR), biomarkers, and motor indicators directly from medical PDF reports.
          </p>

          <div className="inline-flex items-center justify-center px-6 py-3.5 border border-transparent text-sm font-bold rounded-xl text-white bg-blue-600 group-hover:bg-blue-700 transition-colors w-full shadow-sm">
            Upload PDF Clinical Report
          </div>
        </button>

        {/* Card 2: Interactive Questionnaire */}
        <button
          onClick={() => onSelectAction("questionnaire")}
          className="group relative bg-white border border-slate-200 rounded-3xl p-8 text-left flex flex-col h-full hover:border-emerald-500 hover:shadow-lg transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-emerald-500 cursor-pointer shadow-xs"
        >
          <div className="flex items-center justify-between mb-6">
            <div className="bg-emerald-50 border border-emerald-200 w-14 h-14 rounded-2xl flex items-center justify-center group-hover:bg-emerald-600 group-hover:border-emerald-600 transition-colors duration-300">
              <ClipboardList className="w-7 h-7 text-emerald-600 group-hover:text-white transition-colors duration-300" />
            </div>
            <span className="text-xs font-semibold uppercase tracking-wider text-emerald-700 bg-emerald-50 border border-emerald-200 px-3 py-1 rounded-full">
              Interactive Guided
            </span>
          </div>

          <h3 className="text-2xl font-extrabold text-slate-900 mb-3 group-hover:text-emerald-600 transition-colors">
            Answer Questionnaire
          </h3>
          <p className="text-slate-600 flex-grow mb-8 text-sm sm:text-base leading-relaxed">
            Answer structured clinical screening questionnaires tailored specifically for Alzheimer’s disease or Parkinson’s disease.
          </p>

          <div className="inline-flex items-center justify-center px-6 py-3.5 border border-transparent text-sm font-bold rounded-xl text-white bg-emerald-600 group-hover:bg-emerald-700 transition-colors w-full shadow-sm">
            Start Questionnaire Screening
          </div>
        </button>
      </div>

      {/* Key Capability Highlights */}
      <div className="grid sm:grid-cols-3 gap-6 max-w-4xl mx-auto border-t border-slate-200 pt-10">
        <div className="flex items-start space-x-4">
          <div className="p-2.5 rounded-xl bg-slate-100 text-indigo-600 border border-slate-200 flex-shrink-0">
            <Cpu className="w-5 h-5" />
          </div>
          <div>
            <h4 className="text-sm font-bold text-slate-900 mb-1">Dual Disease Models</h4>
            <p className="text-xs text-slate-600 leading-normal">
              ADNI Random Forest (Alzheimer's) and PPMI Random Forest (Parkinson's) classifiers.
            </p>
          </div>
        </div>

        <div className="flex items-start space-x-4">
          <div className="p-2.5 rounded-xl bg-slate-100 text-purple-600 border border-slate-200 flex-shrink-0">
            <Shield className="w-5 h-5" />
          </div>
          <div>
            <h4 className="text-sm font-bold text-slate-900 mb-1">SHAP Explainability</h4>
            <p className="text-xs text-slate-600 leading-normal">
              Backend-calculated SHAP feature rankings explaining feature contributions.
            </p>
          </div>
        </div>

        <div className="flex items-start space-x-4">
          <div className="p-2.5 rounded-xl bg-slate-100 text-blue-600 border border-slate-200 flex-shrink-0">
            <BookOpen className="w-5 h-5" />
          </div>
          <div>
            <h4 className="text-sm font-bold text-slate-900 mb-1">RAG & PubMed Evidence</h4>
            <p className="text-xs text-slate-600 leading-normal">
              Retrieval-augmented knowledge base snippets and live PubMed literature references.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

