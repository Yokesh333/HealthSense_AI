import asyncio
import fitz
import json
import logging
from backend.services.llm_service import GroqLLMService

logging.basicConfig(level=logging.INFO)

async def test_pdf(path):
    s = GroqLLMService()
    doc = fitz.open(path)
    text = "\n".join([page.get_text("text") for page in doc])
    try:
        res = await s.extract_clinical_variables(text)
        print(f"=== {path} ===")
        print("patient_information:", json.dumps(res.get("patient_information"), indent=2))
        print("clinical_scores:", json.dumps(res.get("clinical_scores"), indent=2))
    except Exception as e:
        print(f"Error on {path}: {e}")

async def main():
    for pdf in [
        "Sample_pdf/HealthSenseAI_Synthetic_Alzheimer_Clinical_Report.pdf",
        "Sample_pdf/HealthSenseAI_Synthetic_Parkinsons_Clinical_Report.pdf",
        "Sample_pdf/alzheimer.pdf",
        "Sample_pdf/alzheimer_2.pdf",
        "Sample_pdf/parkinson.pdf",
        "Sample_pdf/parkinson_2.pdf"
    ]:
        await test_pdf(pdf)

if __name__ == "__main__":
    asyncio.run(main())
