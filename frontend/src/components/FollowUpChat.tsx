import React, { useState, useRef, useEffect } from 'react';
import { MessageSquare, Send, Loader2, Sparkles, Bot, User } from 'lucide-react';
import { sendFollowUp } from '../services/api';
import type { AgentAnalysisResponse, FollowUpResponse } from '../types/api';

interface FollowUpChatProps {
  initialResult: AgentAnalysisResponse;
}

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  isError?: boolean;
  structured?: FollowUpResponse['structured'];
  evidence?: FollowUpResponse['web_evidence'];
  rag_evidence?: FollowUpResponse['rag_evidence'];
}

const SUGGESTED_QUESTIONS = [
  "What does my result mean?",
  "What lifestyle changes may support brain health?",
  "What food habits may support brain health?",
  "How can I improve my sleep?",
  "What does the research say about exercise?",
  "What are the latest treatment developments?"
];

export const FollowUpChat: React.FC<FollowUpChatProps> = ({ initialResult }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSend = async (text: string) => {
    if (!text.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: text
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const response = await sendFollowUp({
        question: text,
        disease_context: initialResult.disease_context,
        previous_explanation: initialResult.explanation,
        screening_context: {
          workflow: initialResult.workflow,
          prediction: initialResult.prediction,
          questionnaire_profile: initialResult.questionnaire_profile,
          explanation: initialResult.explanation
        }
      });

      const answerText = response.answer || (response as any).response || "I couldn't generate a response right now. Please try again.";

      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: answerText,
        structured: response.structured,
        evidence: response.web_evidence,
        rag_evidence: response.rag_evidence
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error: any) {
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: error.message || "Failed to get a response. Please try again.",
        isError: true
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="mt-10 bg-white rounded-3xl border border-slate-200 overflow-hidden flex flex-col h-[650px] shadow-xs">
      <div className="bg-slate-50 px-6 py-4 border-b border-slate-200 flex items-center justify-between">
        <div className="flex items-center">
          <div className="p-2 bg-blue-50 border border-blue-200 rounded-xl mr-3">
            <MessageSquare className="w-5 h-5 text-blue-600" />
          </div>
          <div>
            <h2 className="text-base font-extrabold text-slate-900">Ask HealthSense AI Assistant</h2>
            <p className="text-xs text-slate-500">
              Interactive clinical follow-up powered by PubMed & biomedical RAG
            </p>
          </div>
        </div>
        <span className="text-[11px] font-bold uppercase tracking-wider text-blue-700 bg-blue-50 border border-blue-200 px-3 py-1 rounded-full flex items-center gap-1.5">
          <Sparkles className="w-3 h-3 text-blue-600" />
          Follow-up Intelligence
        </span>
      </div>

      <div className="flex-grow overflow-y-auto p-6 space-y-6 bg-slate-50/50">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center max-w-md mx-auto space-y-6">
            <div className="w-16 h-16 bg-blue-50 border border-blue-200 rounded-2xl flex items-center justify-center shadow-xs">
              <Bot className="w-8 h-8 text-blue-600" />
            </div>
            <div className="space-y-2">
              <h3 className="text-lg font-bold text-slate-900">Clinical Follow-up Assistant</h3>
              <p className="text-slate-600 text-xs sm:text-sm leading-relaxed">
                Ask specific questions about your screening findings, disease mechanisms, lifestyle habits, or clinical research evidence.
              </p>
            </div>
            <div className="flex flex-wrap justify-center gap-2">
              {SUGGESTED_QUESTIONS.map((q, i) => (
                <button
                  key={i}
                  onClick={() => handleSend(q)}
                  className="px-3.5 py-2 bg-white border border-slate-200 rounded-xl text-xs font-semibold text-slate-700 hover:border-blue-400 hover:text-blue-700 transition-all shadow-2xs cursor-pointer"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        ) : (
          messages.map((msg) => (
            <div key={msg.id} className={`flex items-start gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              {msg.role === 'assistant' && (
                <div className="w-8 h-8 rounded-xl bg-blue-50 border border-blue-200 flex items-center justify-center text-blue-600 flex-shrink-0 mt-1">
                  <Bot className="w-4 h-4" />
                </div>
              )}
              <div className={`max-w-[85%] sm:max-w-[75%] rounded-2xl p-5 ${
                msg.role === 'user' 
                  ? 'bg-blue-600 text-white shadow-xs font-medium' 
                  : msg.isError
                    ? 'bg-rose-50 text-rose-800 border border-rose-200'
                    : 'bg-white border border-slate-200 text-slate-800 shadow-2xs'
              }`}>
                {msg.role === 'assistant' && !msg.isError ? (
                  msg.structured ? (
                    <div className="space-y-3">
                      {msg.structured.title && (
                        <h3 className="text-sm font-extrabold text-slate-900 border-b border-slate-200 pb-2">
                          {msg.structured.title}
                        </h3>
                      )}
                      {msg.structured.summary && (
                        <p className="text-xs text-slate-700 leading-relaxed font-medium">
                          {msg.structured.summary}
                        </p>
                      )}
                      {msg.structured.sections && msg.structured.sections.map((sec, idx) => (
                        <div key={idx} className="bg-slate-50 p-3.5 rounded-xl border border-slate-200 space-y-1.5">
                          <h4 className="text-[11px] font-bold uppercase tracking-wider text-blue-700">
                            {sec.heading}
                          </h4>
                          {sec.content && (
                            <p className="text-xs text-slate-700 leading-relaxed">
                              {sec.content}
                            </p>
                          )}
                          {sec.key_points && sec.key_points.length > 0 && (
                            <ul className="space-y-1 pl-4 list-disc text-xs text-slate-700 pt-1">
                              {sec.key_points.map((kp, kpidx) => (
                                <li key={kpidx} className="leading-snug">{kp}</li>
                              ))}
                            </ul>
                          )}
                        </div>
                      ))}
                      {msg.structured.clinical_notice && (
                        <p className="text-[10px] text-slate-500 italic pt-1 border-t border-slate-200">
                          {msg.structured.clinical_notice}
                        </p>
                      )}
                    </div>
                  ) : (
                    <div className="prose prose-sm max-w-none">
                      <div className="text-[10px] font-bold uppercase tracking-wider text-slate-500 mb-2 border-b border-slate-200 pb-1.5">
                        Evidence-Based Information
                      </div>
                      <p className="whitespace-pre-wrap text-xs sm:text-sm leading-relaxed text-slate-800">
                        {msg.content.replace(/\|/g, '').replace(/<br\s*\/?>/gi, '\n')}
                      </p>
                    </div>
                  )
                ) : (
                  <p className="whitespace-pre-wrap text-xs sm:text-sm leading-relaxed">{msg.content}</p>
                )}

                {msg.rag_evidence && msg.rag_evidence.length > 0 && (
                  <div className="mt-4 pt-3 border-t border-slate-200 space-y-2">
                    <p className="text-[10px] font-bold uppercase tracking-wider text-teal-700">RAG Knowledge Base Citations</p>
                    <ul className="space-y-1.5">
                      {msg.rag_evidence.slice(0, 3).map((rev, i) => (
                        <li key={i} className="text-xs text-slate-700 bg-slate-50 p-2.5 rounded-xl border border-slate-200">
                          <span className="font-bold text-slate-900 block">{rev.source} (Page {rev.page})</span>
                          <span className="text-slate-600 line-clamp-2 text-[11px]">"{rev.text}"</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                
                {msg.evidence && msg.evidence.length > 0 && (
                  <div className="mt-4 pt-3 border-t border-slate-200 space-y-2">
                    <p className="text-[10px] font-bold uppercase tracking-wider text-blue-700">PubMed Research Sources</p>
                    <ul className="space-y-1.5">
                      {msg.evidence.slice(0, 3).map((ev, i) => (
                        <li key={i} className="text-xs text-slate-700 bg-slate-50 p-2.5 rounded-xl border border-slate-200">
                          <a href={ev.url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline font-bold block truncate">
                            {ev.title}
                          </a>
                          <span className="text-slate-500 text-[11px]">{ev.source} • {ev.published_date}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
              {msg.role === 'user' && (
                <div className="w-8 h-8 rounded-xl bg-blue-600 flex items-center justify-center text-white flex-shrink-0 mt-1 shadow-2xs">
                  <User className="w-4 h-4" />
                </div>
              )}
            </div>
          ))
        )}
        {isLoading && (
          <div className="flex justify-start items-center space-x-3">
            <div className="w-8 h-8 rounded-xl bg-blue-50 border border-blue-200 flex items-center justify-center text-blue-600 flex-shrink-0">
              <Bot className="w-4 h-4" />
            </div>
            <div className="bg-white border border-slate-200 rounded-2xl px-5 py-3.5 shadow-2xs flex items-center space-x-3">
              <Loader2 className="w-4 h-4 text-blue-600 animate-spin" />
              <span className="text-slate-600 text-xs font-semibold">Retrieving biomedical research evidence...</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="p-4 bg-slate-50 border-t border-slate-200">
        <form 
          onSubmit={(e) => {
            e.preventDefault();
            handleSend(inputValue);
          }}
          className="relative flex items-center"
        >
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Ask a question about your analysis or evidence..."
            disabled={isLoading}
            className="w-full pl-5 pr-14 py-3.5 bg-white border border-slate-300 rounded-2xl text-slate-900 placeholder-slate-400 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all disabled:opacity-50 shadow-2xs"
          />
          <button
            type="submit"
            disabled={isLoading || !inputValue.trim()}
            className="absolute right-2 p-2.5 bg-blue-600 text-white rounded-xl hover:bg-blue-700 disabled:opacity-50 disabled:hover:bg-blue-600 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 cursor-pointer"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
      </div>
    </div>
  );
};

