import React from 'react';
import type { WebSearchResult } from '../types/api';
import { Globe, ExternalLink, Library } from 'lucide-react';

interface Props {
  evidence: WebSearchResult[];
}

const WebEvidenceList: React.FC<Props> = ({ evidence }) => {
  if (!evidence || evidence.length === 0) return null;

  return (
    <div className="bg-white rounded-3xl border border-slate-200 overflow-hidden mb-6 shadow-xs">
      <div className="bg-slate-50 px-6 py-4 border-b border-slate-200 flex items-center justify-between">
        <h2 className="text-base font-extrabold text-slate-900 flex items-center">
          <Globe className="w-5 h-5 mr-2.5 text-blue-600" />
          External Biomedical Literature & PubMed Evidence
        </h2>
        <span className="text-[11px] font-bold uppercase tracking-wider text-blue-700 bg-blue-50 border border-blue-200 px-3 py-1 rounded-full flex items-center gap-1">
          <Library className="w-3 h-3 text-blue-600" />
          PubMed Query Engine
        </span>
      </div>
      
      <div className="p-6">
        <div className="space-y-4">
          {evidence.map((item, index) => (
            <div key={index} className="border border-slate-200 rounded-2xl p-5 bg-slate-50 hover:bg-slate-100/70 transition-colors space-y-3">
              <a 
                href={item.url} 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-base font-bold text-blue-600 hover:text-blue-800 flex items-start justify-between group leading-snug"
              >
                <span>{item.title}</span>
                <ExternalLink className="w-4 h-4 ml-2 mt-1 text-slate-400 group-hover:text-blue-600 transition-colors flex-shrink-0" />
              </a>
              
              <div className="flex flex-wrap items-center gap-2 text-xs font-semibold">
                <span className="bg-blue-50 text-blue-800 border border-blue-200 px-2.5 py-1 rounded-lg">
                  {item.source || "PubMed External Source"}
                </span>
                {item.published_date && (
                  <span className="bg-white text-slate-700 px-2.5 py-1 rounded-lg border border-slate-200 shadow-2xs">
                    Published: {item.published_date}
                  </span>
                )}
                {item.trust_indicator && (
                  <span className="bg-emerald-50 text-emerald-800 border border-emerald-200 px-2.5 py-1 rounded-lg">
                    {item.trust_indicator}
                  </span>
                )}
              </div>
              
              <p className="text-sm text-slate-700 leading-relaxed">
                {item.snippet}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default WebEvidenceList;

