import React from 'react';
import { ShieldAlert } from 'lucide-react';

const LimitationsDisclaimer: React.FC = () => {
  return (
    <div className="bg-slate-100 text-slate-700 rounded-2xl p-6 mt-8 border border-slate-200 shadow-2xs">
      <div className="flex items-start">
        <ShieldAlert className="w-6 h-6 text-rose-600 mr-3 flex-shrink-0 mt-1" />
        <div>
          <h3 className="text-slate-900 font-semibold mb-2">Research prototype classification — not a medical diagnosis.</h3>
          <p className="text-sm leading-relaxed mb-4">
            HealthSense AI is a research prototype that combines machine-learning classification, biomedical retrieval, current PubMed evidence, and LLM-based synthesis. Outputs are intended for research and educational purposes and must not be used as a substitute for professional medical diagnosis or treatment.
          </p>
          <ul className="text-xs list-disc pl-4 space-y-1 text-slate-600">
            <li>ADNI dataset is limited to the project's selected cohort.</li>
            <li>Dementia labels were operationally mapped to AD.</li>
            <li>MOCA has substantial missingness (handled by imputation).</li>
            <li>AD class is smaller than CN/MCI.</li>
            <li>PubMed availability depends on external network access.</li>
            <li>LLM-generated synthesis may contain errors.</li>
            <li>System is a research prototype and not a clinical diagnostic tool.</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default LimitationsDisclaimer;
