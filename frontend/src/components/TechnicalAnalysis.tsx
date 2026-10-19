import React, { useState } from 'react';
import { ChevronDown, ChevronUp, Cpu, Network, Database, Layers, Info } from 'lucide-react';
import AgentWorkflow from './AgentWorkflow';
import ProbabilityChart from './ProbabilityChart';
import EvidenceList from './EvidenceList';
import WebEvidenceList from './WebEvidenceList';
import type { AgentAnalysisResponse } from '../types/api';

interface TechnicalAnalysisProps {
  result: AgentAnalysisResponse;
}

export const TechnicalAnalysis: React.FC<TechnicalAnalysisProps> = ({ result }) => {
  const [isExpanded, setIsExpanded] = useState(true);

  return (
    <div className="mt-10 bg-white rounded-3xl border border-slate-200 overflow-hidden shadow-xs">
      <button 
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full px-6 py-4 flex items-center justify-between bg-slate-50 hover:bg-slate-100/80 transition-colors border-b border-slate-200 cursor-pointer"
      >
        <div className="flex items-center text-slate-900 font-extrabold text-lg">
          <Cpu className="w-5 h-5 mr-3 text-blue-600" />
          Technical & Scientific Analysis
        </div>
        <div className="flex items-center text-xs font-semibold text-slate-600 bg-white border border-slate-200 px-3 py-1.5 rounded-full shadow-xs">
          <span className="mr-2">Machine Learning & Agent Details</span>
          {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </div>
      </button>

      {isExpanded && (
        <div className="p-6 sm:p-8 space-y-10">
          
          {/* Agent Execution Workflow */}
          <div>
            <h3 className="text-sm font-bold uppercase tracking-wider text-blue-700 mb-4 flex items-center">
              <Network className="w-4 h-4 mr-2" />
              Multi-Agent Execution Pipeline
            </h3>
            <AgentWorkflow agentsExecuted={result.agents_executed} />
          </div>

          {/* ADNI Alzheimer's Model Prediction / Probabilities */}
          {result.prediction && (
            <div>
              <h3 className="text-sm font-bold uppercase tracking-wider text-purple-700 mb-4 flex items-center">
                <Database className="w-4 h-4 mr-2" />
                Alzheimer's Model Inference (ADNI Random Forest)
              </h3>
              <div className="bg-slate-50 p-6 rounded-2xl border border-slate-200 space-y-4">
                <div className="flex flex-wrap items-center gap-4 text-xs text-slate-700 pb-4 border-b border-slate-200">
                  <div>
                    <span className="text-slate-500 font-medium">Predicted Class: </span>
                    <span className="font-extrabold text-purple-900 bg-purple-50 border border-purple-200 px-2.5 py-1 rounded-lg">
                      {result.prediction.class}
                    </span>
                  </div>
                  {result.model && (
                    <div>
                      <span className="text-slate-500 font-medium">Model Specs: </span>
                      <span className="font-mono text-purple-700 font-bold">
                        {result.model.name} v{result.model.version}
                      </span>
                    </div>
                  )}
                </div>
                <ProbabilityChart probabilities={result.prediction.probabilities} />
              </div>
            </div>
          )}

          {/* ADNI SHAP Explainability (Backend-Driven Only) */}
          {(result.prediction || result.explainability) && (() => {
            const adniExpl = result.explainability || result.prediction?.explainability;
            const hasShapData = Boolean(adniExpl && adniExpl.top_features && adniExpl.top_features.length > 0);

            return (
              <div>
                <h3 className="text-sm font-bold uppercase tracking-wider text-purple-700 mb-1 flex items-center">
                  <Cpu className="w-4 h-4 mr-2" />
                  Alzheimer's SHAP Feature Explainability
                </h3>
                <p className="text-xs text-slate-600 mb-4">
                  Patient-level TreeExplainer feature attributions quantifying each clinical feature's contribution toward or away from the predicted diagnosis.
                </p>

                {hasShapData && adniExpl ? (
                  <div className="bg-slate-50 p-6 rounded-2xl border border-slate-200 space-y-4">
                    <div className="flex flex-wrap items-center gap-4 text-xs text-slate-700 pb-3 border-b border-slate-200 font-mono">
                      <span>Method: <strong className="text-slate-900">{adniExpl.method || "SHAP"}</strong></span>
                      <span>Model: <strong className="text-slate-900">{adniExpl.model_type || "RandomForestClassifier"}</strong></span>
                      <span>Base Value: <strong className="text-slate-900">{typeof adniExpl.base_value === 'number' ? adniExpl.base_value.toFixed(4) : (adniExpl.base_value ?? "—")}</strong></span>
                    </div>

                    <div className="overflow-x-auto">
                      <table className="w-full text-left font-mono text-xs text-slate-800 bg-white rounded-xl border border-slate-200 overflow-hidden shadow-xs">
                        <thead>
                          <tr className="bg-slate-100 border-b border-slate-200 text-slate-600 font-bold uppercase text-[10px] tracking-wider">
                            <th className="p-3">Feature Name</th>
                            <th className="p-3">Input Value</th>
                            <th className="p-3">SHAP Attribution</th>
                            <th className="p-3">Directional Impact</th>
                            <th className="p-3 min-w-[120px]">Contribution Magnitude</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-100">
                          {(() => {
                            const adniMaxShap = Math.max(...adniExpl.top_features.map((f) => Math.abs(f.shap_value) || 0.0001));
                            return adniExpl.top_features.slice(0, 5).map((item, idx) => {
                              const isPositive = item.shap_value >= 0;
                              const shapStr = isPositive ? `+${item.shap_value.toFixed(4)}` : item.shap_value.toFixed(4);
                              const predCls = result.prediction?.class || result.prediction?.predicted_class || "AD";
                              const dirStr = isPositive ? `Toward ${predCls} (+)` : `Away from ${predCls} (-)`;
                              const valStr = item.feature_value === null || item.feature_value === undefined ? "—" : String(item.feature_value);
                              const pct = Math.min(100, Math.max(10, Math.round((Math.abs(item.shap_value) / adniMaxShap) * 100)));

                              return (
                                <tr key={idx} className="hover:bg-slate-50 transition-colors">
                                  <td className="p-3 font-bold text-slate-900">{item.feature}</td>
                                  <td className="p-3 text-slate-600">
                                    {item.feature_value === null || item.feature_value === undefined ? (
                                      <span className="text-slate-400 italic">Missing / Imputed</span>
                                    ) : (
                                      <span className="font-semibold text-slate-800">{valStr}</span>
                                    )}
                                  </td>
                                  <td className="p-3">
                                    <span className={`inline-flex items-center px-2 py-0.5 rounded-md text-xs font-bold ${
                                      isPositive 
                                        ? "bg-rose-50 text-rose-700 border border-rose-200" 
                                        : "bg-emerald-50 text-emerald-700 border border-emerald-200"
                                    }`}>
                                      {shapStr}
                                    </span>
                                  </td>
                                  <td className="p-3">
                                    <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold ${
                                      isPositive 
                                        ? "bg-rose-50/80 text-rose-800 border border-rose-200/80" 
                                        : "bg-emerald-50/80 text-emerald-800 border border-emerald-200/80"
                                    }`}>
                                      <span className={`w-1.5 h-1.5 rounded-full ${isPositive ? "bg-rose-500" : "bg-emerald-500"}`} />
                                      {dirStr}
                                    </span>
                                  </td>
                                  <td className="p-3">
                                    <div className="flex items-center gap-2">
                                      <div className="flex-1 bg-slate-100 rounded-full h-2 overflow-hidden border border-slate-200">
                                        <div 
                                          className={`h-full rounded-full transition-all duration-300 ${isPositive ? "bg-rose-500" : "bg-emerald-500"}`}
                                          style={{ width: `${pct}%` }}
                                        />
                                      </div>
                                      <span className="text-[10px] text-slate-400 font-sans">{pct}%</span>
                                    </div>
                                  </td>
                                </tr>
                              );
                            });
                          })()}
                        </tbody>
                      </table>
                    </div>

                    <div className="text-[11px] text-slate-600 space-y-1 bg-white p-3.5 rounded-xl border border-slate-200">
                      <div className="flex flex-wrap items-center gap-4 text-xs pb-2 border-b border-slate-100">
                        <span className="inline-flex items-center gap-1.5 text-rose-700 font-bold">
                          <span className="w-2 h-2 rounded-full bg-rose-500" />
                          Positive SHAP (+): Increases risk toward {result.prediction?.class || result.prediction?.predicted_class || "target disease class"}
                        </span>
                        <span className="inline-flex items-center gap-1.5 text-emerald-700 font-bold">
                          <span className="w-2 h-2 rounded-full bg-emerald-500" />
                          Negative SHAP (-): Decreases risk (shifts toward Cognitively Normal)
                        </span>
                      </div>
                      <p className="text-[10px] text-slate-500 italic pt-1 mt-1">
                        Clinical Disclaimer: SHAP values describe patient-level feature contributions to the machine learning model prediction. They represent statistical attributions, not causal biological factors, and do not constitute a medical diagnosis.
                      </p>
                    </div>
                  </div>
                ) : (
                  <div className="bg-slate-50 p-5 rounded-2xl border border-slate-200 text-slate-600 text-xs flex items-start gap-3">
                    <Info className="w-4 h-4 text-purple-600 mt-0.5 shrink-0" />
                    <div>
                      <span className="font-bold text-slate-800 block mb-0.5">SHAP Explainability Unavailable</span>
                      <span>
                        Patient-level SHAP feature attributions were not returned by the backend service for this analysis. Model probabilities and inference remain fully valid.
                      </span>
                    </div>
                  </div>
                )}
              </div>
            );
          })()}

          {/* Parkinson's Model Prediction / Probabilities */}
          {result.parkinson_prediction && (
            <div>
              <h3 className="text-sm font-bold uppercase tracking-wider text-teal-700 mb-4 flex items-center">
                <Database className="w-4 h-4 mr-2" />
                Parkinson's Model Inference (PPMI Random Forest)
              </h3>
              <div className="bg-slate-50 p-6 rounded-2xl border border-slate-200 space-y-4">
                <div className="flex flex-wrap items-center gap-4 text-xs text-slate-700 pb-4 border-b border-slate-200">
                  <div>
                    <span className="text-slate-500 font-medium">Predicted Class: </span>
                    <span className="font-extrabold text-teal-900 bg-teal-50 border border-teal-200 px-2.5 py-1 rounded-lg">
                      {result.parkinson_prediction.predicted_label}
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-500 font-medium">Model Specs: </span>
                    <span className="font-mono text-teal-700 font-bold">
                      {result.parkinson_prediction.model_name} v{result.parkinson_prediction.model_version}
                    </span>
                  </div>
                  {result.parkinson_prediction.feature_availability && (
                    <div>
                      <span className="text-slate-500 font-medium">Feature Completeness: </span>
                      <span className="font-mono text-emerald-700 font-bold">
                        {result.parkinson_prediction.feature_availability.present_features_count} / 17 present ({Math.round(result.parkinson_prediction.feature_availability.feature_completeness_ratio * 100)}%)
                      </span>
                    </div>
                  )}
                </div>
                <ProbabilityChart probabilities={result.parkinson_prediction.probabilities} />
              </div>
            </div>
          )}

          {/* Parkinson's SHAP Explainability (Backend-Driven Only) */}
          {(result.parkinson_prediction || result.parkinson_explainability) && (() => {
            const parkinsonExpl = result.parkinson_explainability || result.parkinson_prediction?.explainability;
            const hasShapData = Boolean(parkinsonExpl && parkinsonExpl.top_features && parkinsonExpl.top_features.length > 0);

            return (
              <div>
                <h3 className="text-sm font-bold uppercase tracking-wider text-teal-700 mb-1 flex items-center">
                  <Cpu className="w-4 h-4 mr-2" />
                  Parkinson's SHAP Feature Explainability
                </h3>
                <p className="text-xs text-slate-600 mb-4">
                  Patient-level TreeExplainer feature attributions quantifying each motor and non-motor score's contribution toward or away from Parkinson's Disease.
                </p>

                {hasShapData && parkinsonExpl ? (
                  <div className="bg-slate-50 p-6 rounded-2xl border border-slate-200 space-y-4">
                    <div className="flex flex-wrap items-center gap-4 text-xs text-slate-700 pb-3 border-b border-slate-200 font-mono">
                      <span>Method: <strong className="text-slate-900">{parkinsonExpl.method || "SHAP TreeExplainer"}</strong></span>
                      <span>Model: <strong className="text-slate-900">{parkinsonExpl.model_type || "RandomForestClassifier"}</strong></span>
                      <span>Base Value: <strong className="text-slate-900">{typeof parkinsonExpl.base_value === 'number' ? parkinsonExpl.base_value.toFixed(4) : (parkinsonExpl.base_value ?? "—")}</strong></span>
                    </div>

                    <div className="overflow-x-auto">
                      <table className="w-full text-left font-mono text-xs text-slate-800 bg-white rounded-xl border border-slate-200 overflow-hidden shadow-xs">
                        <thead>
                          <tr className="bg-slate-100 border-b border-slate-200 text-slate-600 font-bold uppercase text-[10px] tracking-wider">
                            <th className="p-3">Feature Name</th>
                            <th className="p-3">Input Value</th>
                            <th className="p-3">SHAP Attribution</th>
                            <th className="p-3">Directional Impact</th>
                            <th className="p-3 min-w-[120px]">Contribution Magnitude</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-100">
                          {(() => {
                            const parkinsonMaxShap = Math.max(...parkinsonExpl.top_features.map((f) => Math.abs(f.shap_value) || 0.0001));
                            return parkinsonExpl.top_features.slice(0, 5).map((item, idx) => {
                              const isPositive = item.shap_value >= 0;
                              const shapStr = isPositive ? `+${item.shap_value.toFixed(4)}` : item.shap_value.toFixed(4);
                              const dirStr = isPositive ? "Toward Parkinson's (+)" : "Away from Parkinson's (-)";
                              const valStr = item.feature_value === null || item.feature_value === undefined ? "—" : String(item.feature_value);
                              const pct = Math.min(100, Math.max(10, Math.round((Math.abs(item.shap_value) / parkinsonMaxShap) * 100)));

                              return (
                                <tr key={idx} className="hover:bg-slate-50 transition-colors" title={item.explanation || undefined}>
                                  <td className="p-3">
                                    <div className="font-bold text-slate-900">{item.feature}</div>
                                    {item.explanation && (
                                      <div className="text-[10px] text-slate-500 font-sans line-clamp-1">{item.explanation}</div>
                                    )}
                                  </td>
                                  <td className="p-3 text-slate-600">
                                    {item.feature_value === null || item.feature_value === undefined ? (
                                      <span className="text-slate-400 italic">Missing (Imputed)</span>
                                    ) : (
                                      <span className="font-semibold text-slate-800">{valStr}</span>
                                    )}
                                  </td>
                                  <td className="p-3">
                                    <span className={`inline-flex items-center px-2 py-0.5 rounded-md text-xs font-bold ${
                                      isPositive 
                                        ? "bg-rose-50 text-rose-700 border border-rose-200" 
                                        : "bg-emerald-50 text-emerald-700 border border-emerald-200"
                                    }`}>
                                      {shapStr}
                                    </span>
                                  </td>
                                  <td className="p-3">
                                    <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold ${
                                      isPositive 
                                        ? "bg-rose-50/80 text-rose-800 border border-rose-200/80" 
                                        : "bg-emerald-50/80 text-emerald-800 border border-emerald-200/80"
                                    }`}>
                                      <span className={`w-1.5 h-1.5 rounded-full ${isPositive ? "bg-rose-500" : "bg-emerald-500"}`} />
                                      {dirStr}
                                    </span>
                                  </td>
                                  <td className="p-3">
                                    <div className="flex items-center gap-2">
                                      <div className="flex-1 bg-slate-100 rounded-full h-2 overflow-hidden border border-slate-200">
                                        <div 
                                          className={`h-full rounded-full transition-all duration-300 ${isPositive ? "bg-rose-500" : "bg-emerald-500"}`}
                                          style={{ width: `${pct}%` }}
                                        />
                                      </div>
                                      <span className="text-[10px] text-slate-400 font-sans">{pct}%</span>
                                    </div>
                                  </td>
                                </tr>
                              );
                            });
                          })()}
                        </tbody>
                      </table>
                    </div>

                    <div className="text-[11px] text-slate-600 space-y-1 bg-white p-3.5 rounded-xl border border-slate-200">
                      <div className="flex flex-wrap items-center gap-4 text-xs pb-2 border-b border-slate-100">
                        <span className="inline-flex items-center gap-1.5 text-rose-700 font-bold">
                          <span className="w-2 h-2 rounded-full bg-rose-500" />
                          Positive SHAP (+): Increases risk toward Parkinson's Disease
                        </span>
                        <span className="inline-flex items-center gap-1.5 text-emerald-700 font-bold">
                          <span className="w-2 h-2 rounded-full bg-emerald-500" />
                          Negative SHAP (-): Decreases risk (shifts toward Healthy Control)
                        </span>
                      </div>
                      {parkinsonExpl.aggregation_note && (
                        <p className="text-[10px] text-slate-500 pt-1">
                          Note: {parkinsonExpl.aggregation_note}
                        </p>
                      )}
                      <p className="text-[10px] text-slate-500 italic pt-1 border-t border-slate-200 mt-2">
                        Clinical Disclaimer: SHAP values describe patient-level feature contributions to the machine learning model prediction. They represent statistical attributions, not causal biological factors, and do not constitute a medical diagnosis.
                      </p>
                    </div>
                  </div>
                ) : (
                  <div className="bg-slate-50 p-5 rounded-2xl border border-slate-200 text-slate-600 text-xs flex items-start gap-3">
                    <Info className="w-4 h-4 text-teal-600 mt-0.5 shrink-0" />
                    <div>
                      <span className="font-bold text-slate-800 block mb-0.5">SHAP Explainability Unavailable</span>
                      <span>
                        Patient-level SHAP feature attributions were not returned by the backend service for this analysis. Model probabilities and inference remain fully valid.
                      </span>
                    </div>
                  </div>
                )}
              </div>
            );
          })()}

          {/* Questionnaire Data Breakdown */}
          {result.workflow === "QUESTIONNAIRE" && result.questionnaire_profile && (
            <div>
              <h3 className="text-sm font-bold uppercase tracking-wider text-amber-700 mb-4 flex items-center">
                <Layers className="w-4 h-4 mr-2" />
                Raw Questionnaire Profile Structure
              </h3>
              <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 overflow-x-auto shadow-xs">
                <pre className="text-xs text-emerald-400 font-mono">
                  {JSON.stringify(result.questionnaire_profile, null, 2)}
                </pre>
              </div>
            </div>
          )}

          {/* RAG Evidence */}
          {result.evidence && result.evidence.length > 0 && (
            <div>
              <EvidenceList evidence={result.evidence} diseaseContext={result.disease_context} />
            </div>
          )}

          {/* Web Evidence */}
          {result.web_evidence && result.web_evidence.length > 0 && (
            <div>
              <WebEvidenceList evidence={result.web_evidence} />
            </div>
          )}

        </div>
      )}
    </div>
  );
};

