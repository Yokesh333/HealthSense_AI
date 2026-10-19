import React, { useState, useEffect } from 'react';
import { ArrowRight, ArrowLeft, Loader2, Info, CheckCircle2 } from 'lucide-react';
import { getQuestionnaire, submitUnifiedAnalysis } from '../services/api';
import type { QuestionnaireData, AgentAnalysisResponse, ScreeningType } from '../types/api';
import { clearQuestionnaireSessionState } from '../services/sessionStorage';

interface QuestionnaireFormProps {
  type: ScreeningType;
  onBack: () => void;
  onComplete: (response: AgentAnalysisResponse) => void;
}

export const QuestionnaireForm: React.FC<QuestionnaireFormProps> = ({ type, onBack, onComplete }) => {
  const [data, setData] = useState<QuestionnaireData | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const [currentIndex, setCurrentIndex] = useState(() => {
    try {
      const savedIndex = sessionStorage.getItem(`healthsense_index_${type}`);
      return savedIndex ? parseInt(savedIndex, 10) : 0;
    } catch {
      return 0;
    }
  });
  
  const [answers, setAnswers] = useState<Record<string, number>>(() => {
    try {
      const savedAnswers = sessionStorage.getItem(`healthsense_answers_${type}`);
      return savedAnswers ? JSON.parse(savedAnswers) : {};
    } catch {
      return {};
    }
  });

  useEffect(() => {
    const loadQuestionnaire = async () => {
      try {
        setLoading(true);
        const qData = await getQuestionnaire(type);
        setData(qData);
      } catch (err: any) {
        setError(err.message || "Failed to load questions.");
      } finally {
        setLoading(false);
      }
    };
    loadQuestionnaire();
  }, [type]);

  const saveStateToSession = (newAnswers: Record<string, number>, newIndex: number) => {
    try {
      sessionStorage.setItem(`healthsense_answers_${type}`, JSON.stringify(newAnswers));
      sessionStorage.setItem(`healthsense_index_${type}`, newIndex.toString());
      sessionStorage.setItem('healthsense_active_screening_type', type);
      sessionStorage.setItem('healthsense_active_view', 'questionnaire');
    } catch (e) {
      // Session storage fail-safe
    }
  };

  const clearSessionState = () => {
    clearQuestionnaireSessionState();
  };

  const handleAnswer = (questionId: string, value: number) => {
    setAnswers(prev => {
      const updated = { ...prev, [questionId]: value };
      saveStateToSession(updated, currentIndex);
      return updated;
    });
  };

  const handleNext = () => {
    if (data && currentIndex < data.items.length - 1) {
      const newIndex = currentIndex + 1;
      setCurrentIndex(newIndex);
      saveStateToSession(answers, newIndex);
    }
  };

  const handlePrev = () => {
    if (currentIndex > 0) {
      const newIndex = currentIndex - 1;
      setCurrentIndex(newIndex);
      saveStateToSession(answers, newIndex);
    }
  };

  const handleQuit = () => {
    clearSessionState();
    onBack();
  };

  const handleSubmit = async () => {
    if (!data) return;
    
    setSubmitting(true);
    setError(null);
    try {
      const formattedResponses = Object.entries(answers).map(([qId, optIndex]) => {
        const questionItem = data.items.find(i => i.id === qId);
        const answerText = questionItem?.options.find(o => o.value === optIndex)?.label || "";
        return {
          question_id: qId,
          answer: answerText
        };
      });

      const response = await submitUnifiedAnalysis({
        type: "QUESTIONNAIRE",
        questionnaire_data: {
          questionnaire_id: data.questionnaire_id,
          version: data.version,
          responses: formattedResponses
        },
        disease_context: data.disease_context,
      });
      clearSessionState();
      onComplete(response);
    } catch (err: any) {
      setError(err.message || "An error occurred while submitting.");
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-24 text-center">
        <Loader2 className="w-12 h-12 text-blue-600 animate-spin mb-4" />
        <p className="text-lg font-bold text-slate-900">Loading Clinical Questionnaire...</p>
      </div>
    );
  }

  if (error && !data) {
    return (
      <div className="max-w-2xl mx-auto py-12 px-4 text-center">
        <div className="bg-rose-50 border border-rose-200 text-rose-800 p-6 rounded-2xl mb-6">
          <p className="font-medium">{error}</p>
        </div>
        <button onClick={onBack} className="px-6 py-3 bg-white border border-slate-300 text-slate-700 rounded-xl hover:bg-slate-50 font-semibold text-sm cursor-pointer shadow-xs">
          Return to Selection
        </button>
      </div>
    );
  }

  if (!data || data.items.length === 0) return null;

  const currentItem = data.items[currentIndex];
  const hasAnsweredCurrent = answers[currentItem.id] !== undefined;
  const progressPercentage = ((currentIndex + 1) / data.items.length) * 100;
  
  // Section handling for "Both"
  let sectionTitle = "";
  if (type === "both") {
    if (currentIndex < 10) {
      sectionTitle = "SECTION 1 — MEMORY & THINKING (ADNI PROTOCOL)";
    } else {
      sectionTitle = "SECTION 2 — MOVEMENT & MOBILITY (PPMI PROTOCOL)";
    }
  }

  return (
    <div className="max-w-3xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <button 
          onClick={handleQuit}
          className="flex items-center text-slate-600 hover:text-slate-900 font-medium text-xs sm:text-sm bg-white border border-slate-200 px-3 py-1.5 rounded-xl transition-colors shadow-xs cursor-pointer"
        >
          <ArrowLeft className="w-4 h-4 mr-1.5" />
          Exit Screening
        </button>
        <div className="text-xs font-bold text-slate-600 bg-white border border-slate-200 px-3 py-1.5 rounded-xl shadow-xs">
          Question <span className="text-blue-600 font-extrabold">{currentIndex + 1}</span> of {data.items.length}
        </div>
      </div>

      {/* Progress Meter */}
      <div className="w-full bg-slate-200 rounded-full h-2.5 mb-8 overflow-hidden border border-slate-300">
        <div 
          className="bg-gradient-to-r from-blue-600 to-indigo-600 h-2.5 rounded-full transition-all duration-300 ease-out"
          style={{ width: `${progressPercentage}%` }}
        ></div>
      </div>

      {/* Question Card */}
      <div className="bg-white rounded-3xl border border-slate-200 p-6 sm:p-10 mb-8 min-h-[320px] flex flex-col justify-between shadow-xs">
        <div>
          {sectionTitle && (
            <div className="text-[11px] font-bold tracking-wider text-blue-700 uppercase mb-3 bg-blue-50 border border-blue-200 px-3 py-1 rounded-full inline-block">
              {sectionTitle}
            </div>
          )}
          
          <h3 className="text-xl sm:text-2xl font-extrabold text-slate-900 mb-8 leading-snug">
            {currentItem.question}
          </h3>
        </div>

        <div className="space-y-3">
          {currentItem.options.map((option) => {
            const isSelected = answers[currentItem.id] === option.value;
            return (
              <button
                key={option.value}
                onClick={() => handleAnswer(currentItem.id, option.value)}
                className={`w-full text-left p-4 rounded-2xl border transition-all duration-200 flex items-center justify-between cursor-pointer ${
                  isSelected 
                    ? 'border-blue-500 bg-blue-50/90 text-blue-950 shadow-xs' 
                    : 'border-slate-200 bg-slate-50 hover:border-slate-300 hover:bg-slate-100 text-slate-800'
                }`}
              >
                <div className="flex items-center space-x-3">
                  <div className={`w-5 h-5 rounded-full border flex items-center justify-center flex-shrink-0 ${
                    isSelected ? 'border-blue-600 bg-blue-600' : 'border-slate-400 bg-white'
                  }`}>
                    {isSelected && <div className="w-2 h-2 rounded-full bg-white" />}
                  </div>
                  <span className="font-semibold text-sm sm:text-base">{option.label}</span>
                </div>
                {isSelected && <CheckCircle2 className="w-5 h-5 text-blue-600 flex-shrink-0" />}
              </button>
            );
          })}
        </div>
      </div>

      {/* Controls */}
      <div className="flex justify-between items-center gap-4">
        <button
          onClick={handlePrev}
          disabled={currentIndex === 0 || submitting}
          className={`flex items-center px-5 py-3 rounded-xl font-semibold text-sm transition-colors ${
            currentIndex === 0 
              ? 'text-slate-400 border border-slate-200 bg-slate-100 cursor-not-allowed' 
              : 'text-slate-700 border border-slate-300 bg-white hover:bg-slate-50 shadow-xs cursor-pointer'
          }`}
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Previous
        </button>

        {currentIndex < data.items.length - 1 ? (
          <button
            onClick={handleNext}
            disabled={!hasAnsweredCurrent}
            className={`flex items-center px-7 py-3 rounded-xl font-bold text-sm transition-all ${
              !hasAnsweredCurrent
                ? 'bg-slate-200 text-slate-400 cursor-not-allowed'
                : 'bg-blue-600 text-white hover:bg-blue-700 shadow-sm cursor-pointer'
            }`}
          >
            Next Question
            <ArrowRight className="w-4 h-4 ml-2" />
          </button>
        ) : (
          <button
            onClick={handleSubmit}
            disabled={!hasAnsweredCurrent || submitting}
            className={`flex items-center px-7 py-3 rounded-xl font-bold text-sm transition-all ${
              !hasAnsweredCurrent || submitting
                ? 'bg-slate-200 text-slate-400 cursor-not-allowed'
                : 'bg-emerald-600 text-white hover:bg-emerald-700 shadow-sm cursor-pointer'
            }`}
          >
            {submitting ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Analyzing Answers...
              </>
            ) : (
              <>
                Submit & View Analysis
                <ArrowRight className="w-4 h-4 ml-2" />
              </>
            )}
          </button>
        )}
      </div>

      {error && (
        <div className="mt-6 text-center text-rose-700 bg-rose-50 border border-rose-200 p-4 rounded-xl text-sm font-medium">
          {error}
        </div>
      )}

      {/* Safety Notice */}
      <div className="mt-10 flex items-start bg-slate-100 p-4 rounded-2xl border border-slate-200 space-x-3">
        <Info className="w-5 h-5 text-slate-500 flex-shrink-0 mt-0.5" />
        <p className="text-xs text-slate-600 leading-relaxed">
          This screening is for research-oriented health assessment and does not diagnose Alzheimer's disease or Parkinson's disease or determine disease stage. Please consult a qualified healthcare professional for clinical evaluation.
        </p>
      </div>
    </div>
  );
};

