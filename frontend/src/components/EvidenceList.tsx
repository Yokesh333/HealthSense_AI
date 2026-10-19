import React from 'react';
import type { RAGChunk } from '../types/api';
import { BookOpen, Sparkles } from 'lucide-react';

interface Props {
  evidence: RAGChunk[];
  diseaseContext?: string[];
}

const EvidenceList: React.FC<Props> = ({ evidence, diseaseContext }) => {
  if (!evidence || evidence.length === 0) return null;

  // Determine disease heading based on diseaseContext or retrieved chunks
  const normalizedContext = (diseaseContext || []).map(d => d.toLowerCase());

  let kbTitle = "Biomedical Evidence — Knowledge Base";

  const isParkinsonsCtx = normalizedContext.includes("parkinsons");
  const isAlzheimersCtx = normalizedContext.includes("alzheimers");
  const isBothCtx = normalizedContext.includes("both");

  if (isParkinsonsCtx && !isAlzheimersCtx && !isBothCtx) {
    kbTitle = "Biomedical Evidence — Parkinson's Knowledge Base";
  } else if (isAlzheimersCtx && !isParkinsonsCtx && !isBothCtx) {
    kbTitle = "Biomedical Evidence — Alzheimer's Knowledge Base";
  } else {
    // Inspect chunk metadata if context is ambiguous or unset
    const diseasesInChunks = new Set<string>();
    evidence.forEach(item => {
      if (item.disease) diseasesInChunks.add(item.disease.toLowerCase());
      else if (item.disease_context) diseasesInChunks.add(item.disease_context.toLowerCase());
      else if (item.category) {
        if (item.category.toLowerCase().includes("parkinson")) diseasesInChunks.add("parkinsons");
        if (item.category.toLowerCase().includes("alzheimer")) diseasesInChunks.add("alzheimers");
      }
    });

    if (diseasesInChunks.has("parkinsons") && !diseasesInChunks.has("alzheimers")) {
      kbTitle = "Biomedical Evidence — Parkinson's Knowledge Base";
    } else if (diseasesInChunks.has("alzheimers") && !diseasesInChunks.has("parkinsons")) {
      kbTitle = "Biomedical Evidence — Alzheimer's Knowledge Base";
    } else {
      kbTitle = "Biomedical Evidence — Knowledge Base";
    }
  }

  return (
    <div className="bg-white rounded-3xl border border-slate-200 overflow-hidden mb-6 shadow-xs">
      <div className="bg-slate-50 px-6 py-4 border-b border-slate-200 flex items-center justify-between">
        <h2 className="text-base font-extrabold text-slate-900 flex items-center">
          <BookOpen className="w-5 h-5 mr-2.5 text-teal-600" />
          {kbTitle}
        </h2>
        <span className="text-[11px] font-bold uppercase tracking-wider text-teal-700 bg-teal-50 border border-teal-200 px-3 py-1 rounded-full flex items-center gap-1">
          <Sparkles className="w-3 h-3 text-teal-600" />
          Internal RAG Index
        </span>
      </div>
      
      <div className="p-6">
        <div className="space-y-4">
          {evidence.map((item, index) => (
            <div key={index} className="border border-slate-200 rounded-2xl p-5 bg-slate-50 hover:bg-slate-100/70 transition-colors space-y-3">
              <div className="flex flex-wrap items-center gap-2 text-xs font-semibold">
                <span className="bg-white text-slate-800 px-2.5 py-1 rounded-lg border border-slate-200 shadow-2xs">Source: {item.source}</span>
                {item.category && <span className="bg-teal-50 text-teal-800 border border-teal-200 px-2.5 py-1 rounded-lg">{item.category}</span>}
                <span className="bg-white text-slate-800 px-2.5 py-1 rounded-lg border border-slate-200 shadow-2xs">Page {item.page}</span>
                <span className="bg-blue-50 text-blue-800 border border-blue-200 px-2.5 py-1 rounded-lg ml-auto font-mono">
                  Relevance: {(item.score * 100).toFixed(1)}%
                </span>
              </div>
              <p className="text-sm text-slate-700 leading-relaxed italic border-l-2 border-teal-600 pl-3">
                "{item.text}"
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default EvidenceList;

