import abc
import json
import logging
from typing import Any, Dict, List

from groq import AsyncGroq
from backend.config import GROQ_API_KEY, GROQ_MODEL, LLM_MAX_TOKENS, LLM_TEMPERATURE

logger = logging.getLogger(__name__)

class BaseLLMService(abc.ABC):
    @abc.abstractmethod
    async def generate_explanation(self, prompt: str, workflow: str = "CLINICAL_REPORT") -> Dict[str, Any]:
        pass

    @abc.abstractmethod
    async def extract_clinical_variables(self, text: str) -> Dict[str, Any]:
        pass

    @abc.abstractmethod
    async def generate_followup_response(self, prompt: str, chat_history: List[Dict[str, str]], workflow: str = "CLINICAL_REPORT") -> Any:
        pass


class GroqLLMService(BaseLLMService):
    def __init__(self):
        if not GROQ_API_KEY:
            logger.warning("GROQ_API_KEY is not set. GroqLLMService will fail if called.")
        self.client = AsyncGroq(api_key=GROQ_API_KEY, max_retries=0)
        self.model = GROQ_MODEL

    async def generate_explanation(self, prompt: str, workflow: str = "CLINICAL_REPORT") -> Dict[str, Any]:
        if not GROQ_API_KEY:
            return self._fallback_response("Groq API key is missing. LLM synthesis is unavailable.")

        import time
        t0 = time.time()
        logger.info(f"[ANALYZE] Groq LLM API request started (model={self.model}, workflow={workflow})")

        if workflow == "QUESTIONNAIRE":
            system_prompt = (
                "You are HealthSense AI, a patient-friendly biomedical evidence synthesis assistant.\n\n"
                "STRICT QUESTIONNAIRE SCREENING RULES:\n"
                "1. QUESTIONNAIRE FINDINGS ARE AUTHORITATIVE: Base synthesis strictly on self-reported questionnaire answers.\n"
                "   - If questionnaire_score is 0 or positive_findings is empty: 'Your responses did not indicate the memory and thinking difficulties assessed by this questionnaire. This screening result does not diagnose or rule out Alzheimer\\'s disease.'\n"
                "2. DO NOT MENTION CLINICAL REPORTS: Never mention clinical reports, imaging, MRI, MoCA, MMSE, UPDRS, ADNI ML predictions, or SHAP unless explicitly part of the questionnaire submission.\n"
                "3. RAG EVIDENCE IS BACKGROUND MEDICAL LITERATURE ONLY: Do NOT interpret literature as personal symptoms.\n"
                "4. NO DIAGNOSTIC CLAIMS: End with 'This is an AI-assisted screening/research result and is not a medical diagnosis.'\n\n"
                "Return valid JSON matching expected structure."
            )
        else:
            system_prompt = (
                "You are HealthSense AI, a patient-friendly biomedical evidence synthesis assistant.\n\n"
                "STRICT CLINICAL REPORT ANALYSIS RULES:\n"
                "1. THIS IS A CLINICAL PDF REPORT WORKFLOW: Base synthesis strictly on the extracted report findings and ADNI research ML prediction.\n"
                "2. NEVER MENTION QUESTIONNAIRE RESPONSES: There are NO questionnaire responses in this workflow. NEVER write 'your responses did not indicate' or 'questionnaire answers'.\n"
                "3. MODEL PROBABILITY PHRASING: Format model predictions using source-attributed phrasing:\n"
                "   - 'The ADNI-based Random Forest assigned an X% predicted probability to the [Class] class.'\n"
                "   - DO NOT call that percentage the patient's personal probability or likelihood of disease.\n"
                "4. SOURCE-ATTRIBUTED WORDING:\n"
                "   - Use: 'The uploaded report describes...', 'The model assigned...', 'The reported imaging findings include...', 'Biomedical evidence indicates...'.\n"
                "   - DO NOT write: 'You have Alzheimer\\'s disease', 'This confirms Alzheimer\\'s', 'This proves Alzheimer\\'s', 'high likelihood of Alzheimer\\'s disease', 'typical Alzheimer\\'s changes', or 'consistent with the typical pattern of Alzheimer\\'s disease'.\n"
                "5. NO DIAGNOSTIC CLAIMS: State clearly that the prediction is a machine-learning research prediction and not a medical diagnosis.\n"
                "6. End with: 'This is an AI-assisted screening/research result and is not a medical diagnosis.'\n\n"
                "Return valid JSON matching expected structure."
            )

        json_structure_prompt = (
            "\nExpected JSON structure:\n"
            "{\n"
            '  "what_results_suggest": "...",\n'
            '  "why_relevant": "...",\n'
            '  "what_research_says": ["..."],\n'
            '  "next_steps": ["..."],\n'
            '  "clinical_notice": "This is an AI-assisted screening/research result and is not a medical diagnosis."\n'
            "}"
        )

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt + json_structure_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=LLM_TEMPERATURE,
                max_tokens=LLM_MAX_TOKENS,
                response_format={"type": "json_object"},
            )

            dur = time.time() - t0
            logger.info(f"[ANALYZE] Groq LLM API call completed in {dur:.3f}s")

            content = response.choices[0].message.content
            if not content:
                raise ValueError("Received empty content from Groq.")
            
            # Normalize non-standard Unicode punctuation to standard ASCII
            content = (
                content.replace("\u2011", "-")
                .replace("\u2013", "-")
                .replace("\u2014", "-")
                .replace("\u2018", "'")
                .replace("\u2019", "'")
                .replace("\u201c", '"')
                .replace("\u201d", '"')
                .replace("\u00a0", " ")
            )
            
            parsed = json.loads(content)
            return parsed

        except Exception as e:
            dur = time.time() - t0
            logger.error(f"[ANALYZE] Groq LLM API failed after {dur:.3f}s — exception_type={type(e).__name__}, detail={e}")
            return self._fallback_response("LLM synthesis is currently unavailable.")

    async def check_connection(self) -> Dict[str, Any]:
        """
        Minimal internal health check to verify Groq API connectivity and model response parsing.
        """
        if not GROQ_API_KEY:
            return {"status": "unavailable", "reason": "GROQ_API_KEY environment variable is missing."}
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Return exactly: HealthSense AI LLM connection successful."}],
                max_tokens=20,
                temperature=0.0,
            )
            content = response.choices[0].message.content or ""
            return {
                "status": "connected",
                "model": self.model,
                "response": content.strip()
            }
        except Exception as e:
            logger.error("GroqLLMService health check failed: %s (%s)", e, type(e).__name__)
            return {"status": "error", "model": self.model, "reason": f"{type(e).__name__}: {str(e)}"}


    async def extract_clinical_variables(self, text: str) -> Dict[str, Any]:
        if not GROQ_API_KEY:
            raise ValueError("Groq API key is missing.")

        system_prompt = (
            "You are a clinical data extraction assistant for HealthSense AI.\n"
            "Extract structured clinical information from the provided report into STRICT JSON.\n\n"
            "EXPECTED JSON STRUCTURE:\n"
            "{\n"
            '  "disease_context": ["alzheimers"] | ["parkinsons"] | ["alzheimers", "parkinsons"] | ["unknown"],\n'
            '  "patient_information": {\n'
            '    "age": number | null,\n'
            '    "sex": string | null,\n'
            '    "education": total formal education years (number | null),\n'
            '    "race": string | null,\n'
            '    "ethnicity": string | null\n'
            "  },\n"
            '  "clinical_scores": {\n'
            '    "mmse": number | null,\n'
            '    "moca": number | null,\n'
            '    "cdr": number | null,\n'
            '    "adas": number | null,\n'
            '    "faq": number | null,\n'
            '    "updrs": number | null,\n'
            '    "hoehn_yahr": string | null,\n'
            '    "other_scores": {}\n'
            "  },\n"
            '  "cognitive_findings": {\n'
            '    "memory_impairment": boolean | null,\n'
            '    "executive_dysfunction": boolean | null,\n'
            '    "language_deficits": boolean | null,\n'
            '    "details": [string]\n'
            "  },\n"
            '  "motor_findings": {\n'
            '    "resting_tremor": boolean | null,\n'
            '    "bradykinesia": boolean | null,\n'
            '    "rigidity": boolean | null,\n'
            '    "gait_postural_instability": boolean | null,\n'
            '    "details": [string]\n'
            "  },\n"
            '  "symptoms": [string],\n'
            '  "duration": string | null,\n'
            '  "imaging_findings": [{"modality": string, "finding": string, "source_page": number | null}],\n'
            '  "laboratory_findings": [string],\n'
            '  "medications": [string],\n'
            '  "family_history": [string],\n'
            '  "clinical_impression": string | null,\n'
            '  "source_pages": {},\n'
            '  "missing_information": [string]\n'
            "}\n\n"
            "STRICT RULES:\n"
            "1. DO NOT fabricate or infer missing values. If a score or field is not stated in the report, set it to null or empty list.\n"
            "2. EDUCATION EXTRACTION RULE:\n"
            "   - Extract education as total cumulative completed years of formal education (number | null).\n"
            "   - Only calculate/infer a total when the preceding education level/duration is explicitly established:\n"
            "     * '16 years of education' -> 16\n"
            "     * 'completed college + 1 year graduate school' -> 17\n"
            "     * 'high school graduate' -> 12\n"
            "     * 'bachelor degree' / 'college graduate' -> 16\n"
            "   - If only a standalone postgraduate duration is stated without establishing preceding college/high school completion (e.g., 'one year of graduate school' with no prior education context), set education to null.\n"
            "   - DO NOT extract a standalone single digit like 1 for 'one year of graduate school'.\n"
            "   - Do not fabricate or assume missing education years.\n"
            "3. Determine disease_context explicitly from report evidence:\n"
            "   - Alzheimer-related: memory decline, MMSE/MoCA/CDR/ADAS, hippocampal atrophy, Alzheimer impression.\n"
            "   - Parkinson-related: resting tremor, bradykinesia, rigidity, UPDRS, Hoehn & Yahr, DaTSCAN, Parkinson impression.\n"
            "   - Use ['alzheimers', 'parkinsons'] only if explicit evidence for BOTH exists.\n"
            "   - If insufficient disease evidence exists, return ['unknown'].\n"
            "4. Extract page numbers where findings or scores appear (e.g. source_page from '--- PAGE X ---' markers).\n"
            "5. Ignore patient names, DOB, addresses, MRNs, or any PII.\n"
            "6. Return strictly valid JSON."
        )

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            temperature=0.0,
            max_tokens=2048,
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content
        if not content:
            raise ValueError("Received empty content from Groq extraction.")
        return json.loads(content)

    async def generate_followup_response(
        self, prompt: str, chat_history: List[Dict[str, str]], workflow: str = "CLINICAL_REPORT"
    ) -> Dict[str, Any]:
        if not GROQ_API_KEY:
            return self._fallback_followup_response("LLM service is unavailable.")

        if workflow == "QUESTIONNAIRE":
            rule_3 = (
                "3. For 'What does my result mean?' or result-related questions:\n"
                "   - Translate questionnaire findings into simple, everyday language.\n"
                "   - Frame results strictly using questionnaire context: 'Your responses indicated...', 'Your questionnaire score reflects...'.\n"
                "   - NEVER mention clinical reports, MRI, imaging, MoCA, MMSE, UPDRS, ADNI, or SHAP unless explicitly part of the questionnaire submission.\n"
            )
        else:
            rule_3 = (
                "3. For 'What does my result mean?' or result-related questions:\n"
                "   - Explain the uploaded clinical report findings and research model prediction in plain language.\n"
                "   - Use source-attributed phrasing: 'The uploaded clinical report describes...', 'The model assigned a predicted probability of...', 'The reported imaging findings include...'.\n"
                "   - NEVER write 'your questionnaire responses', 'your responses did not indicate', or 'all answers were Never'. There are NO questionnaire responses in this workflow.\n"
                "   - Explain that model predictions are AI-assisted research estimates and not medical diagnoses.\n"
            )

        system_prompt = (
            "You are HealthSense AI, an empathetic, patient-friendly health assistant.\n"
            "You must return strictly valid JSON matching the following structure:\n"
            "{\n"
            '  "response_type": "lifestyle" | "food" | "sleep" | "result_explanation" | "current_research" | "general",\n'
            '  "title": "Clear Patient-Friendly Title",\n'
            '  "summary": "Short, clear 1-2 sentence overview in plain language.",\n'
            '  "sections": [\n'
            '    {\n'
            '      "heading": "Section Heading",\n'
            '      "content": "Explanatory paragraph in plain language.",\n'
            '      "key_points": ["Actionable point 1", "Actionable point 2"]\n'
            '    }\n'
            '  ],\n'
            '  "evidence_note": "Short note on research/evidence grounding.",\n'
            '  "clinical_notice": "This information is general and does not replace advice from a healthcare professional."\n'
            "}\n\n"
            "STRICT RULES:\n"
            "1. DO NOT use ASCII tables (no '|' or '----'), raw HTML tags (no '<br>'), or raw markdown table markup in JSON strings.\n"
            "2. DO NOT mention software internal terms: vector database, embeddings, internal API routes, or raw code variables.\n"
            f"{rule_3}"
            "4. For lifestyle/food/sleep/research questions:\n"
            "   - Provide 2 to 4 clear sections with concise, practical bullet points.\n"
            "   - Use cautious evidence-based language ('may support', 'is associated with').\n"
            "5. Keep responses concise, compassionate, structured, and readable for normal patients."
        )

        messages = [{"role": "system", "content": system_prompt}]
        for msg in chat_history:
            messages.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})
            
        messages.append({"role": "user", "content": prompt})

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=LLM_TEMPERATURE,
                max_tokens=LLM_MAX_TOKENS,
                response_format={"type": "json_object"},
            )
            raw_content = response.choices[0].message.content
            if not raw_content:
                return self._fallback_followup_response("No response content generated.")
            parsed = json.loads(raw_content)
            return parsed
        except Exception as e:
            logger.error("GroqLLMService followup error: %s", str(e))
            return self._fallback_followup_response("An error occurred while generating the response. Please try again.")

    def _fallback_followup_response(self, message: str) -> Dict[str, Any]:
        return {
            "response_type": "general",
            "title": "HealthSense AI Response",
            "summary": message,
            "sections": [
                {
                    "heading": "General Information",
                    "content": "We were unable to generate a detailed structured response at this moment.",
                    "key_points": [
                        "Please try submitting your question again.",
                        "Consult a qualified healthcare provider for personal health concerns."
                    ]
                }
            ],
            "evidence_note": "HealthSense AI evidence service.",
            "clinical_notice": "This information is general and does not replace advice from a healthcare professional."
        }

    def _fallback_response(self, summary_msg: str) -> Dict[str, Any]:
        return {
            "what_results_suggest": summary_msg,
            "why_relevant": "Information is limited.",
            "what_research_says": [],
            "next_steps": [
                "Consider discussing with a healthcare professional."
            ],
            "clinical_notice": "This is an AI-assisted screening/research result and is not a medical diagnosis."
        }
