import React from 'react';
import { FileCheck, ArrowRight, ArrowLeft, Activity, Info, User, Brain, Stethoscope, Pill } from 'lucide-react';
import type { StructuredClinicalProfile } from '../types/api';

interface ExtractedReportDataProps {
  data: StructuredClinicalProfile;
  onSubmit: () => void;
  onCancel: () => void;
}

export const ExtractedReportData: React.FC<ExtractedReportDataProps> = ({ data, onSubmit, onCancel }) => {
  
  const displayValue = (val: any) => {
    if (val === null || val === undefined || val === "" || (Array.isArray(val) && val.length === 0)) {
      return <span className="text-slate-400 italic text-xs">Not reported in document</span>;
    }
    if (Array.isArray(val)) {
      return (
        <ul className="list-disc list-inside space-y-1 text-slate-800 font-medium text-xs sm:text-sm text-left">
          {val.map((item, idx) => (
            <li key={idx}>{typeof item === 'object' ? `${item.modality || ''}: ${item.finding || ''}` : item}</li>
          ))}
        </ul>
      );
    }
    return <span className="text-slate-900 font-semibold text-xs sm:text-sm">{String(val)}</span>;
  };

  const getDiseaseLabel = (ctx: string[]) => {
    if (!ctx || ctx.length === 0 || ctx.includes("unknown")) return "Unknown / General Context";
    if (ctx.includes("alzheimers") && ctx.includes("parkinsons")) return "Combined (Alzheimer's & Parkinson's Evidence)";
    if (ctx.includes("alzheimers")) return "Alzheimer's Disease Context";
    if (ctx.includes("parkinsons")) return "Parkinson's Disease Context";
    return ctx.join(", ");
  };

  const p = data.patient_information || {};
  const sc = data.clinical_scores || {};
  const cog = data.cognitive_findings || {};
  const mot = data.motor_findings || {};

  return (
    <div className="max-w-4xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="text-center mb-8 space-y-3">
        <div className="bg-emerald-50 border border-emerald-200 w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-3 shadow-xs">
          <FileCheck className="w-8 h-8 text-emerald-600" />
        </div>
        <h2 className="text-3xl font-extrabold text-slate-900 tracking-tight">
          Extracted Clinical Profile
        </h2>
        <p className="text-slate-600 max-w-lg mx-auto text-sm sm:text-base leading-relaxed">
          Review the extracted clinical scores, symptoms, and biomarkers before proceeding to dual model analysis.
        </p>
      </div>

      {/* Explicit Notice Banner */}
      <div className="bg-blue-50 border border-blue-200 rounded-2xl p-4 mb-8 flex items-start space-x-3">
        <Info className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
        <div>
          <h4 className="text-xs font-bold uppercase tracking-wider text-blue-800">Extracted Document Data</h4>
          <p className="text-xs text-slate-700 mt-0.5 leading-relaxed">
            This screen displays structured clinical data parsed directly from your PDF document. It does not represent an AI diagnosis.
          </p>
        </div>
      </div>

      <div className="bg-white rounded-3xl border border-slate-200 overflow-hidden mb-8 divide-y divide-slate-100 shadow-xs">
        
        {/* Detected Context Pill */}
        <div className="px-6 py-4 bg-slate-50 flex flex-col sm:flex-row justify-between items-start sm:items-center">
          <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Detected Clinical Context</span>
          <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-blue-50 border border-blue-200 text-blue-800 mt-1 sm:mt-0">
            <Activity className="w-3.5 h-3.5 mr-1.5 text-blue-600" />
            {getDiseaseLabel(data.disease_context)}
          </span>
        </div>

        {/* Demographics Card */}
        <div className="p-6">
          <h3 className="text-xs font-bold text-blue-700 uppercase tracking-wider mb-4 flex items-center">
            <User className="w-4 h-4 mr-2" />
            Patient Demographics
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="bg-slate-50 p-3.5 rounded-xl border border-slate-200">
              <span className="text-slate-500 block text-[11px] font-medium mb-1">Age</span>
              {displayValue(p.age)}
            </div>
            <div className="bg-slate-50 p-3.5 rounded-xl border border-slate-200">
              <span className="text-slate-500 block text-[11px] font-medium mb-1">Sex</span>
              {displayValue(p.sex)}
            </div>
            <div className="bg-slate-50 p-3.5 rounded-xl border border-slate-200">
              <span className="text-slate-500 block text-[11px] font-medium mb-1">Education</span>
              {displayValue(p.education ? `${p.education} years` : null)}
            </div>
          </div>
        </div>

        {/* Clinical & Examination Scores */}
        <div className="p-6">
          <h3 className="text-xs font-bold text-purple-700 uppercase tracking-wider mb-4 flex items-center">
            <Brain className="w-4 h-4 mr-2" />
            Clinical & Cognitive Scores
          </h3>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="bg-slate-50 p-3.5 rounded-xl border border-slate-200">
              <span className="text-slate-500 block text-[11px] font-medium mb-1">MMSE (0-30)</span>
              {displayValue(sc.mmse)}
            </div>
            <div className="bg-slate-50 p-3.5 rounded-xl border border-slate-200">
              <span className="text-slate-500 block text-[11px] font-medium mb-1">MoCA (0-30)</span>
              {displayValue(sc.moca)}
            </div>
            <div className="bg-slate-50 p-3.5 rounded-xl border border-slate-200">
              <span className="text-slate-500 block text-[11px] font-medium mb-1">CDR Score</span>
              {displayValue(sc.cdr)}
            </div>
            <div className="bg-slate-50 p-3.5 rounded-xl border border-slate-200">
              <span className="text-slate-500 block text-[11px] font-medium mb-1">UPDRS Total</span>
              {displayValue(sc.updrs)}
            </div>
          </div>
        </div>

        {/* Reported Symptoms & Findings */}
        <div className="p-6">
          <h3 className="text-xs font-bold text-teal-700 uppercase tracking-wider mb-4 flex items-center">
            <Stethoscope className="w-4 h-4 mr-2" />
            Symptoms & Examination Findings
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="bg-slate-50 p-4 rounded-xl border border-slate-200">
              <span className="text-slate-500 block text-[11px] font-medium mb-1.5">Symptoms & Duration</span>
              {displayValue(data.symptoms)}
              <div className="mt-2 pt-2 border-t border-slate-200">
                <span className="text-slate-500 text-[11px]">Duration: </span>
                {displayValue(data.duration)}
              </div>
            </div>
            <div className="bg-slate-50 p-4 rounded-xl border border-slate-200">
              <span className="text-slate-500 block text-[11px] font-medium mb-1.5">Cognitive & Motor Details</span>
              <div className="space-y-2">
                <div>
                  <span className="text-slate-500 text-[11px] block">Cognitive:</span>
                  {displayValue(cog.details)}
                </div>
                <div>
                  <span className="text-slate-500 text-[11px] block">Motor:</span>
                  {displayValue(mot.details)}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Imaging, Labs & Medications */}
        <div className="p-6">
          <h3 className="text-xs font-bold text-emerald-700 uppercase tracking-wider mb-4 flex items-center">
            <Pill className="w-4 h-4 mr-2" />
            Diagnostics, Labs & Medications
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="bg-slate-50 p-4 rounded-xl border border-slate-200">
              <span className="text-slate-500 block text-[11px] font-medium mb-1.5">Imaging & Lab Findings</span>
              <div className="space-y-2">
                <div>
                  <span className="text-slate-500 text-[11px] block">Imaging (MRI / DaTSCAN):</span>
                  {displayValue(data.imaging_findings)}
                </div>
                <div>
                  <span className="text-slate-500 text-[11px] block">Laboratory:</span>
                  {displayValue(data.laboratory_findings)}
                </div>
              </div>
            </div>
            <div className="bg-slate-50 p-4 rounded-xl border border-slate-200">
              <span className="text-slate-500 block text-[11px] font-medium mb-1.5">Medications & History</span>
              <div className="space-y-2">
                <div>
                  <span className="text-slate-500 text-[11px] block">Current Medications:</span>
                  {displayValue(data.medications)}
                </div>
                <div>
                  <span className="text-slate-500 text-[11px] block">Family History:</span>
                  {displayValue(data.family_history)}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Clinical Impression */}
        {data.clinical_impression && (
          <div className="p-6 bg-amber-50 border-t border-amber-200">
            <h3 className="text-xs font-bold text-amber-800 uppercase tracking-wider mb-1">Reported Impression</h3>
            <p className="text-sm text-slate-800 italic font-medium">"{data.clinical_impression}"</p>
          </div>
        )}

      </div>

      {/* Action Buttons */}
      <div className="flex flex-col-reverse sm:flex-row justify-between items-center gap-4">
        <button 
          onClick={onCancel}
          className="flex items-center text-slate-700 hover:text-slate-900 transition-colors text-sm font-medium px-4 py-3 border border-slate-300 rounded-xl bg-white w-full sm:w-auto justify-center shadow-xs cursor-pointer"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Choose Another PDF
        </button>
        <button 
          onClick={onSubmit}
          className="flex items-center justify-center px-8 py-3.5 bg-blue-600 text-white rounded-xl hover:bg-blue-700 font-bold text-sm transition-colors shadow-sm w-full sm:w-auto group cursor-pointer"
        >
          Proceed to HealthSense AI Analysis
          <ArrowRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
        </button>
      </div>
    </div>
  );
};

