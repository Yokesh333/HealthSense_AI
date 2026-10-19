    # Phase 6 Biomedical Source Audit

    Generated: 2026-09-01 16:02 UTC

    ## 1. Biomedical Files Discovered

    **Source directory:** `RAG_Train/`
    **Total PDF files:** 44
    **Total size:** 109.8 MB

    ## 2. File Types

    All source documents are PDF files (`.pdf`). No TXT, CSV, or JSON
    biomedical knowledge files were found in `RAG_Train/`.

    ## 3. Alzheimer's Documents (22 files, 38.5 MB)

    **Status: INCLUDED in Phase 6 knowledge base.**

    | File | Category | Size |
    |---|---|---|
    | `diag1.pdf` | Alzheimerss/Diagnosis | 1501 KB |
| `diag2.pdf` | Alzheimerss/Diagnosis | 470 KB |
| `diag3.pdf` | Alzheimerss/Diagnosis | 1823 KB |
| `diag4.pdf` | Alzheimerss/Diagnosis | 2024 KB |
| `diag5.pdf` | Alzheimerss/Diagnosis | 14871 KB |
| `mri1.pdf` | Alzheimerss/MRI | 886 KB |
| `mri2.pdf` | Alzheimerss/MRI | 302 KB |
| `mri3.pdf` | Alzheimerss/MRI | 717 KB |
| `mri4.pdf` | Alzheimerss/MRI | 1450 KB |
| `mri5.pdf` | Alzheimerss/MRI | 1747 KB |
| `treat3.pdf` | Alzheimerss/Treatments | 1199 KB |
| `treat4.pdf` | Alzheimerss/Treatments | 1119 KB |
| `treatment1.pdf` | Alzheimerss/Treatments | 4436 KB |
| `treatment2.pdf` | Alzheimerss/Treatments | 221 KB |
| `bio1.pdf` | Alzheimerss/biomarkers | 1565 KB |
| `bio2.pdf` | Alzheimerss/biomarkers | 2886 KB |
| `bio3.pdf` | Alzheimerss/biomarkers | 265 KB |
| `bio4.pdf` | Alzheimerss/biomarkers | 184 KB |
| `bio5.pdf` | Alzheimerss/biomarkers | 502 KB |
| `guidelines1.pdf` | Alzheimerss/guidelines | 320 KB |
| `guidelines2.pdf` | Alzheimerss/guidelines | 752 KB |
| `alzheimer's guidelines.pdf` | Alzheimers/General | 154 KB |

    ## 4. Parkinson's Documents (22 files, 71.3 MB)

    **Status: EXCLUDED from Phase 6.** Parkinson's module deferred to a future phase.

    | File | Category | Size |
    |---|---|---|
    | `A guide to thinking changes in parkinsons.pdf` | Parkinsons/General | 2223 KB |
| `diag1.pdf` | Parkinsons/Diagnosis | 787 KB |
| `diag2.pdf` | Parkinsons/Diagnosis | 601 KB |
| `diag3.pdf` | Parkinsons/Diagnosis | 1491 KB |
| `diag4.pdf` | Parkinsons/Diagnosis | 161 KB |
| `parkinson's foundation.pdf` | Parkinsons/Diagnosis | 2477 KB |
| `handwriting1.pdf` | Parkinsons/Handwriting | 803 KB |
| `writing2.pdf` | Parkinsons/Handwriting | 1948 KB |
| `writing3.pdf` | Parkinsons/Handwriting | 3319 KB |
| `MRI_1.pdf` | Parkinsons/MRI | 324 KB |
| `MRI_2.pdf` | Parkinsons/MRI | 693 KB |
| `MRI_3.pdf` | Parkinsons/MRI | 144 KB |
| `MRI_4.pdf` | Parkinsons/MRI | 5027 KB |
| `Intl J Lang   Comm Disor - 2025 - Brzoskowski dos Santos - Speech Characteristics Across Motor Subtypes of Parkinson s.pdf` | Parkinsons/Speech | 663 KB |
| `speech1.pdf` | Parkinsons/Speech | 939 KB |
| `speech2.pdf` | Parkinsons/Speech | 356 KB |
| `06732ed1-aa1c-42e9-be7f-2f08a349b897.pdf` | Parkinsons/Treatment | 23001 KB |
| `ijms-23-09361-v2.pdf` | Parkinsons/Treatment | 2735 KB |
| `parkinson_exercise.pdf` | Parkinsons/Treatment | 442 KB |
| `treatment2.pdf` | Parkinsons/Treatment | 4803 KB |
| `treatment_parkinson.pdf` | Parkinsons/Treatment | 1521 KB |
| `parkinson_.pdf` | Parkinsons/General | 18580 KB |

    ## 5. Content Type Assessment

    The Alzheimer's documents cover:
    - **Diagnosis**: Clinical criteria, cognitive assessment tools (MMSE, ADAS, CDR, MOCA)
    - **MRI**: Structural imaging findings in Alzheimer's disease
    - **Treatments**: Pharmacological and non-pharmacological interventions
    - **Biomarkers**: Amyloid, tau, and other biomarker research
    - **Guidelines**: Clinical practice guidelines

    All documents are biomedical research papers and clinical guidelines — suitable for RAG.

    ## 6. Suitability for Biomedical RAG

    **Suitable: YES**

    - Documents contain rich biomedical text (clinical studies, guidelines, reviews)
    - Text is extractable via PyMuPDF (no image-only PDFs identified in audit)
    - Thematic coverage is coherent with ADNI ML feature set (cognitive assessments, clinical markers)
    - Volume is appropriate for all-MiniLM-L6-v2 embedding and FAISS CPU index

    ## 7. Existing RAG Components

    At the time of this audit:
    - `backend/rag/` — empty (no existing code)
    - `data/knowledge_base/` — empty (no existing embeddings or vector store)
    - No FAISS index found
    - No existing embedding files found

    ## 8. Existing Dependencies (at audit time)

    Not yet installed:
    - `sentence-transformers` — needed for embedding generation
    - `faiss-cpu` — needed for vector similarity search
    - `PyMuPDF` — needed for PDF text extraction

    Already installed:
    - `numpy`, `pandas`, `scipy`, `pydantic`, `fastapi`

    ## 9. Recommended Ingestion Strategy

    1. Recursively scan `RAG_Train/Alzheimer's/` + root-level Alzheimer's PDF
    2. Extract text page-by-page using PyMuPDF
    3. Clean text (whitespace normalisation, line-break repair)
    4. Chunk with 400-word windows, 80-word overlap
    5. Embed with `all-MiniLM-L6-v2`, batch size 64, L2-normalised
    6. Build `faiss.IndexFlatIP` (inner product ≡ cosine for normalised embeddings)
    7. Save index + metadata to `data/knowledge_base/vector_store/`

    ## 10. Recommended Embedding Model

    **`sentence-transformers/all-MiniLM-L6-v2`**

    Reasons:
    - 384-dimensional embeddings (small, fast FAISS index)
    - Strong semantic search performance on scientific text
    - ~22 MB model download; runs on CPU
    - No GPU required
    - No cloud dependency

    ## 11. Recommended Vector Database

    **FAISS CPU (`faiss.IndexFlatIP`)**

    Reasons:
    - Local; no server required
    - Exact search (no approximation error at this document volume)
    - Fast enough for ~23 PDFs worth of chunks
    - L2-normalised embeddings make inner product = cosine similarity

    ## 12. Potential Problems

    - Some large PDFs (diag5.pdf ~15 MB, parkinson_.pdf ~19 MB) may contain
      multi-column layouts that PyMuPDF extracts linearly — text ordering may
      be imperfect but generally usable
    - No Parkinson's content in Phase 6 knowledge base — queries about
      Parkinson's will return Alzheimer's results (low relevance)
    - No LLM in Phase 6 — retrieval returns raw text excerpts, not summaries

    ## 13. Final Recommendation

    **Proceed with Phase 6 Alzheimer's-only ingestion.**

    All 22 Alzheimer's documents are suitable for biomedical RAG.
    The technology stack (PyMuPDF + sentence-transformers + FAISS) is appropriate
    and lightweight. Parkinson's integration should be deferred to the Parkinson's
    module phase.
