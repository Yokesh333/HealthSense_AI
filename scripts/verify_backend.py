import json
import logging
from pathlib import Path
from backend.rag.vector_store import load_index
from backend.rag.retriever import Retriever

PROJECT_ROOT = Path(__file__).resolve().parent.parent
VECTOR_STORE_DIR = PROJECT_ROOT / "data" / "knowledge_base" / "vector_store"
ALZ_JSON = PROJECT_ROOT / "data" / "questionnaire" / "alzheimers_questions.json"
PD_JSON = PROJECT_ROOT / "data" / "questionnaire" / "parkinsons_questions.json"

def verify_rag():
    print("=== RAG VERIFICATION ===")
    index, metadata = load_index()
    
    total_chunks = len(metadata)
    alz_chunks = 0
    pd_chunks = 0
    alz_docs = set()
    pd_docs = set()
    alz_pages = set()
    pd_pages = set()
    
    for m in metadata:
        disease = m.get("disease", "")
        doc = m.get("source", "")
        page = m.get("page", 0)
        if disease == "alzheimers":
            alz_chunks += 1
            alz_docs.add(doc)
            alz_pages.add(f"{doc}_{page}")
        elif disease == "parkinsons":
            pd_chunks += 1
            pd_docs.add(doc)
            pd_pages.add(f"{doc}_{page}")
            
    print(f"Total chunks: {total_chunks}")
    print(f"Alzheimer's chunk count: {alz_chunks}")
    print(f"Parkinson's chunk count: {pd_chunks}")
    print(f"Alzheimer's document count: {len(alz_docs)}")
    print(f"Parkinson's document count: {len(pd_docs)}")
    print(f"Alzheimer's page count: {len(alz_pages)}")
    print(f"Parkinson's page count: {len(pd_pages)}")
    print(f"Embedding dimension: {index.d}")
    print(f"Vector index type: {type(index).__name__}")
    
    diseases = set(m.get("disease", "") for m in metadata)
    print(f"Valid diseases found: {diseases}")
    if "" in diseases or None in diseases:
        print("ERROR: Missing or empty disease in metadata!")
        
def verify_disease_filters():
    print("=== DISEASE FILTER TEST ===")
    from backend.main import app
    import asyncio
    from fastapi.testclient import TestClient
    
    # Force app startup to initialize services
    with TestClient(app) as client:
        rag_service = app.state.rag_service
        
        print("1. Alzheimer's query:")
        res_alz = rag_service.retrieve("memory loss and cognitive decline", top_k=3, disease="alzheimers")
        for r in res_alz:
            print(f"  [{r.disease}] {r.source} - Score: {r.score:.4f}")
        
        print("2. Parkinson's query:")
        res_pd = rag_service.retrieve("handwriting changes tremor and movement problems", top_k=3, disease="parkinsons")
        for r in res_pd:
            print(f"  [{r.disease}] {r.source} - Score: {r.score:.4f}")
            
        print("3. Both queries:")
        res_both = rag_service.retrieve("loss and problems", top_k=10, disease="both")
        diseases_in_both = set(r.disease for r in res_both)
        print(f"  Diseases retrieved for 'both': {diseases_in_both}")

def verify_questionnaires():
    print("=== QUESTIONNAIRE VERIFICATION ===")
    with open(ALZ_JSON, "r") as f:
        alz = json.load(f)
    with open(PD_JSON, "r") as f:
        pd = json.load(f)
        
    print(f"Alzheimer's questions: {len(alz['questions'])}")
    print(f"Parkinson's questions: {len(pd['questions'])}")
    
    print("=== QUESTION QUALITY TRACEABILITY ===")
    all_q = alz['questions'] + pd['questions']
    for q in all_q:
        print(f"ID: {q['id']}, Disease: {q.get('disease')}, Domain: {q.get('domain')}, Concept: {q.get('clinical_concept')}")
        print(f"Source: {q.get('source_document')}")

if __name__ == "__main__":
    verify_rag()
    verify_disease_filters()
    verify_questionnaires()
