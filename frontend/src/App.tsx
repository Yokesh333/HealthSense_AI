import { useState, useEffect } from 'react';
import { Activity, ShieldAlert, Sparkles } from 'lucide-react';


import type { StructuredClinicalProfile, AgentAnalysisResponse, ScreeningType } from './types/api';
import { clearQuestionnaireSessionState, clearReportSessionState, clearAllHealthSenseSession } from './services/sessionStorage';

import { LandingPage } from './components/LandingPage';
import { ScreeningTypeSelector } from './components/ScreeningTypeSelector';
import { QuestionnaireForm } from './components/QuestionnaireForm';
import { ReportUpload } from './components/ReportUpload';
import { ExtractedReportData } from './components/ExtractedReportData';
import { ScreeningResult } from './components/ScreeningResult';
import { analyzeReport, checkHealth } from './services/api';

type ViewState = 
  | "landing" 
  | "screening-selector" 
  | "questionnaire" 
  | "report-upload" 
  | "extracted-data-review" 
  | "results";

function App() {
  const [screeningType, setScreeningType] = useState<ScreeningType | null>(() => {
    try {
      const savedType = sessionStorage.getItem('healthsense_active_screening_type');
      return (savedType as ScreeningType) || null;
    } catch {
      return null;
    }
  });

  const [currentView, setCurrentView] = useState<ViewState>(() => {
    try {
      const savedView = sessionStorage.getItem('healthsense_active_view');
      const savedType = sessionStorage.getItem('healthsense_active_screening_type');
      if (savedView === 'questionnaire' && savedType) {
        return 'questionnaire';
      }
      return 'landing';
    } catch {
      return 'landing';
    }
  });

  const [isBackendConnected, setIsBackendConnected] = useState<boolean>(false);
  
  // State for flows
  const [extractedProfile, setExtractedProfile] = useState<StructuredClinicalProfile | null>(null);
  const [result, setResult] = useState<AgentAnalysisResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const checkBackend = async () => {
      const isHealthy = await checkHealth();
      setIsBackendConnected(isHealthy);
    };
    checkBackend();
  }, []);

  const handleReset = () => {
    clearAllHealthSenseSession();
    setCurrentView("landing");
    setScreeningType(null);
    setExtractedProfile(null);
    setResult(null);
    setError(null);
    setLoading(false);
  };

  const handleActionSelect = (action: "report" | "questionnaire") => {
    if (action === "report") {
      // Clear questionnaire state & session storage completely
      clearQuestionnaireSessionState();
      setScreeningType(null);
      setExtractedProfile(null);
      setResult(null);
      setError(null);
      setCurrentView("report-upload");
    } else {
      // Clear report state & session storage completely
      clearReportSessionState();
      setExtractedProfile(null);
      setResult(null);
      setError(null);
      setCurrentView("screening-selector");
    }
  };

  const handleScreeningTypeSelect = (type: ScreeningType) => {
    // Clear report state completely before starting a new questionnaire
    clearReportSessionState();
    setExtractedProfile(null);
    setResult(null);
    try {
      sessionStorage.setItem('healthsense_active_screening_type', type);
      sessionStorage.setItem('healthsense_active_view', 'questionnaire');
    } catch (e) {}
    setScreeningType(type);
    setCurrentView("questionnaire");
  };

  const handleReportExtracted = (data: StructuredClinicalProfile) => {
    // Clear questionnaire state completely when a report is extracted
    clearQuestionnaireSessionState();
    setScreeningType(null);
    setResult(null);
    setExtractedProfile(data);
    setCurrentView("extracted-data-review");
  };

  const handleAnalyzeReport = async () => {
    if (!extractedProfile) return;
    setLoading(true);
    setError(null);
    
    try {
      const response = await analyzeReport(extractedProfile);
      setResult((prev: AgentAnalysisResponse | null) => {
        // Prevent late requests or duplicate API calls (e.g., from double clicks) 
        // that return a fallback response from overwriting a successful LLM synthesis.
        const isPrevSuccess = prev?.explanation && 
          !prev.explanation.what_results_suggest?.includes("unavailable") && 
          !prev.explanation.what_results_suggest?.includes("Fallback");
          
        const isNewFallback = response.explanation?.what_results_suggest?.includes("unavailable") || 
          response.explanation?.what_results_suggest?.includes("Fallback");

        if (isPrevSuccess && isNewFallback) {
          return prev;
        }
        return response;
      });
      setCurrentView("results");
    } catch (err: any) {
      setError(err.message || "An error occurred while analyzing the report.");
    } finally {
      setLoading(false);
    }
  };

  const handleQuestionnaireComplete = (response: AgentAnalysisResponse) => {
    setResult(response);
    setCurrentView("results");
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 font-sans flex flex-col antialiased selection:bg-blue-600 selection:text-white">
      {/* GLOBAL HEADER */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-50 shadow-xs">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3.5 flex justify-between items-center">
          <button 
            onClick={handleReset} 
            className="flex items-center space-x-3 group focus:outline-none rounded-xl p-1 text-left cursor-pointer"
          >
            <div className="bg-blue-600 p-2 rounded-xl group-hover:scale-105 transition-transform shadow-sm shadow-blue-600/20">
              <Activity className="w-5 h-5 text-white" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="text-lg font-black text-slate-900 tracking-tight leading-none">HealthSense</span>
                <span className="text-xs font-bold px-1.5 py-0.5 rounded bg-blue-50 border border-blue-200 text-blue-600">AI</span>
              </div>
              <p className="text-[11px] text-slate-500 font-medium tracking-wide">Clinical Intelligence Platform</p>
            </div>
          </button>

          <div className="flex items-center space-x-4">
            <div className={`flex items-center text-xs font-bold px-3 py-1.5 rounded-full border ${
              isBackendConnected 
                ? 'bg-emerald-50 text-emerald-700 border-emerald-200 shadow-xs' 
                : 'bg-rose-50 text-rose-700 border-rose-200'
            }`}>
              <div className={`w-2 h-2 rounded-full mr-2 ${isBackendConnected ? 'bg-emerald-500 animate-pulse' : 'bg-rose-500'}`}></div>
              {isBackendConnected ? 'API Connected' : 'API Offline'}
            </div>
          </div>
        </div>
      </header>

      {/* MAIN CONTAINER */}
      <main className="flex-grow w-full">
        {!isBackendConnected && currentView === "landing" && (
          <div className="bg-rose-50 border-b border-rose-200 text-rose-800 p-3.5 text-center text-xs font-semibold flex items-center justify-center space-x-2">
            <ShieldAlert className="w-4 h-4 text-rose-600" />
            <span>Cannot connect to the FastAPI backend server (http://localhost:8000). Please ensure the python server is running.</span>
          </div>
        )}

        {error && currentView !== "landing" && currentView !== "questionnaire" && (
          <div className="max-w-4xl mx-auto mt-6 px-4">
            <div className="bg-rose-50 border border-rose-200 text-rose-900 p-5 rounded-2xl text-center shadow-xs">
              <p className="font-semibold text-sm text-rose-800">{error}</p>
              <button 
                onClick={handleReset} 
                className="mt-3 inline-flex items-center text-xs font-bold text-rose-700 hover:text-rose-900 underline underline-offset-4 cursor-pointer"
              >
                Return to start screen
              </button>
            </div>
          </div>
        )}

        {loading ? (
          <div className="flex flex-col items-center justify-center py-32 px-4 text-center">
            <div className="relative w-16 h-16 mb-6 flex items-center justify-center">
              <div className="absolute inset-0 border-4 border-slate-200 rounded-full"></div>
              <div className="absolute inset-0 border-4 border-blue-600 rounded-full border-t-transparent animate-spin"></div>
              <Sparkles className="w-6 h-6 text-blue-600" />
            </div>
            <h3 className="text-xl font-bold text-slate-900 mb-2">Analyzing Clinical Profile...</h3>
            <p className="text-slate-600 text-xs sm:text-sm max-w-sm leading-relaxed font-medium">
              Executing FastAPI backend multi-agent pipeline, model predictions, SHAP calculations, and biomedical evidence retrieval.
            </p>
          </div>
        ) : (
          <>
            {currentView === "landing" && (
              <LandingPage onSelectAction={handleActionSelect} />
            )}
            
            {currentView === "screening-selector" && (
              <ScreeningTypeSelector onSelect={handleScreeningTypeSelect} onBack={handleReset} />
            )}
            
            {currentView === "questionnaire" && screeningType && (
              <QuestionnaireForm type={screeningType} onBack={() => setCurrentView("screening-selector")} onComplete={handleQuestionnaireComplete} />
            )}
            
            {currentView === "report-upload" && (
              <ReportUpload onBack={handleReset} onExtracted={handleReportExtracted} />
            )}
            
            {currentView === "extracted-data-review" && extractedProfile && (
              <ExtractedReportData data={extractedProfile} onSubmit={handleAnalyzeReport} onCancel={() => setCurrentView("report-upload")} />
            )}
            
            {currentView === "results" && result && (
              <ScreeningResult result={result} onReset={handleReset} />
            )}
          </>
        )}
      </main>

      {/* FOOTER */}
      <footer className="bg-white border-t border-slate-200 mt-16 py-6 text-slate-500 text-xs text-center">
        <div className="max-w-7xl mx-auto px-4 space-y-2">
          <p className="font-semibold text-slate-700">
            HealthSense AI — Research Prototype & Multimodal Clinical Intelligence System
          </p>
          <p className="text-slate-500 max-w-3xl mx-auto leading-relaxed">
            Screening results are provided for research and informational purposes only. SHAP feature importances describe model contributions and do not imply medical causation or clinical diagnosis.
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;

