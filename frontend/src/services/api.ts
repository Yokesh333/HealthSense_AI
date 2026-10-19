import axios from "axios";
import type { 
  StructuredClinicalProfile,
  AgentAnalysisResponse,
  QuestionnaireData,
  UnifiedAnalysisRequest,
  FollowUpRequest,
  FollowUpResponse
} from "../types/api";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

export const checkHealth = async (): Promise<boolean> => {
  try {
    const response = await apiClient.get("/health", { timeout: 3000 });
    return response.status === 200;
  } catch (error) {
    return false;
  }
};

export const getQuestionnaire = async (type: "alzheimers" | "parkinsons" | "both"): Promise<QuestionnaireData> => {
  try {
    const response = await apiClient.get<any>(`/api/questionnaire/${type}`);
    const data = response.data;
    
    let rawQuestions: any[] = [];
    let diseaseContext: string[] = [];
    
    if (type === "both") {
      rawQuestions = [...(data.alzheimers_questions || []), ...(data.parkinsons_questions || [])];
      diseaseContext = ["alzheimers", "parkinsons"];
    } else {
      rawQuestions = data.questions || [];
      diseaseContext = [type];
    }
    
    const items = rawQuestions.map((q: any) => ({
      id: q.id,
      domain: q.domain,
      question: q.question,
      options: (q.answer_options || []).map((opt: string, i: number) => ({
        label: opt,
        value: i
      }))
    }));
    
    return {
      questionnaire_id: data.questionnaire_id,
      version: data.version,
      items,
      disease_context: diseaseContext
    };
  } catch (error: any) {
    console.error("API Error in getQuestionnaire:", error);
    if (axios.isAxiosError(error) && error.response) {
      console.error("Response status:", error.response.status);
      console.error("Response data:", error.response.data);
    }
    throw new Error("Failed to load questionnaire. Please try again.");
  }
};

export const submitUnifiedAnalysis = async (data: UnifiedAnalysisRequest): Promise<AgentAnalysisResponse> => {
  try {
    // The endpoint is still /api/agents/analyze
    const response = await apiClient.post<AgentAnalysisResponse>("/api/agents/analyze", data, { timeout: 30000 });
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      if (error.response?.status === 422) {
        throw new Error("Validation Error: Please check the input format.");
      }
      if (!error.response) {
        throw new Error("Backend unavailable. Please make sure the HealthSense AI API is running.");
      }
    }
    throw new Error("Analysis could not be completed. Please try again.");
  }
};

export const extractReport = async (file: File): Promise<StructuredClinicalProfile> => {
  try {
    const formData = new FormData();
    formData.append("file", file);
    
    const response = await apiClient.post<StructuredClinicalProfile>("/api/reports/extract", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
      timeout: 45000,
    });
    return response.data;
  } catch (error: any) {
    if (axios.isAxiosError(error) && error.response?.data?.detail) {
      throw new Error(error.response.data.detail);
    }
    throw new Error("We couldn't process the report. Please check that it is a text-based PDF under 10 MB and try again.");
  }
};

export const analyzeReport = async (profile: StructuredClinicalProfile, clinicalQuestion?: string): Promise<AgentAnalysisResponse> => {
  try {
    const response = await apiClient.post<AgentAnalysisResponse>("/api/reports/analyze", {
      profile,
      clinical_question: clinicalQuestion || null
    }, { timeout: 45000 });
    return response.data;
  } catch (error: any) {
    if (axios.isAxiosError(error) && error.response?.data?.detail) {
      throw new Error(error.response.data.detail);
    }
    throw new Error("Analysis of the report could not be completed. Please try again.");
  }
};

export const sendFollowUp = async (data: FollowUpRequest): Promise<FollowUpResponse> => {
  try {
    const response = await apiClient.post<FollowUpResponse>("/api/agents/followup", data);
    return response.data;
  } catch (error) {
    throw new Error("Failed to get a response. Please try again.");
  }
};
