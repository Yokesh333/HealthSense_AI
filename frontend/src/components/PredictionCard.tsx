import React from 'react';
import type { MLPrediction } from '../types/api';
import ProbabilityChart from './ProbabilityChart';

interface Props {
  prediction: MLPrediction;
}

const PredictionCard: React.FC<Props> = ({ prediction }) => {
  const getBadgeStyle = (cls: string) => {
    switch (cls) {
      case 'CN': return 'bg-emerald-50 text-emerald-800 border-emerald-200';
      case 'MCI': return 'bg-amber-50 text-amber-800 border-amber-200';
      case 'AD': return 'bg-rose-50 text-rose-800 border-rose-200';
      default: return 'bg-slate-100 text-slate-800 border-slate-200';
    }
  };

  const getLabel = (cls: string) => {
    switch (cls) {
      case 'CN': return 'Cognitively Normal (CN)';
      case 'MCI': return 'Mild Cognitive Impairment (MCI)';
      case 'AD': return 'Alzheimer\'s Disease (AD)';
      default: return cls;
    }
  };

  return (
    <div className="bg-white p-6 rounded-2xl shadow-xs border border-slate-200 mb-6">
      <h2 className="text-lg font-bold text-slate-900 mb-4">Model Classification</h2>
      
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div className="flex-1">
          <div className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Predicted Stage</div>
          <div className={`inline-block px-4 py-2 rounded-xl border font-extrabold text-lg ${getBadgeStyle(prediction.class ?? prediction.predicted_class ?? '')}`}>
            {getLabel(prediction.class ?? prediction.predicted_class ?? '')}
          </div>
        </div>
        
        <div className="flex-1 border-t md:border-t-0 md:border-l border-slate-200 pt-4 md:pt-0 md:pl-6">
          <div className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-3">Probability Distribution</div>
          <ProbabilityChart probabilities={prediction.probabilities} />
        </div>
      </div>
    </div>
  );
};

export default PredictionCard;
