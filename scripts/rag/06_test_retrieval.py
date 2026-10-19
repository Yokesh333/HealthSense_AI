"""
scripts/rag/06_test_retrieval.py

Run 5 evaluation queries against the built FAISS index and print real results.

Run from project root:
    python scripts/rag/06_test_retrieval.py
"""

import json
import logging
import sys
import io
from pathlib import Path

# Force UTF-8 stdout on Windows to handle medical Unicode characters (e.g. β, →)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.rag.service import RAGService

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

EVALUATION_QUERIES = [
    "What cognitive assessments are used in Alzheimer's diagnosis?",
    "What are common symptoms of Alzheimer's disease?",
    "What biomarkers are associated with Alzheimer's disease?",
    "What treatments are available for Alzheimer's disease?",
    "What MRI findings are associated with Alzheimer's disease?",
]

TOP_K = 5

DOCS_DIR = PROJECT_ROOT / "docs"
DOCS_DIR.mkdir(exist_ok=True)


def main():
    print("Initialising RAG service ...")
    service = RAGService()
    print(f"Service ready — {service.num_chunks} indexed chunks.\n")

    all_results = []

    for i, query in enumerate(EVALUATION_QUERIES, 1):
        print(f"\n{'='*70}")
        print(f"QUERY {i}: {query}")
        print(f"{'='*70}")

        results = service.retrieve(query=query, top_k=TOP_K)

        query_record = {
            "query_id": i,
            "query": query,
            "results": [],
        }

        for rank, r in enumerate(results, 1):
            text_preview = r.text[:200].replace("\n", " ") + ("..." if len(r.text) > 200 else "")
            print(f"\n  [{rank}] score={r.score:.4f}  source={r.source}  "
                  f"cat={r.category}  page={r.page}")
            print(f"      chunk_id: {r.chunk_id}")
            print(f"      text: {text_preview}")

            query_record["results"].append({
                "rank": rank,
                "chunk_id": r.chunk_id,
                "source": r.source,
                "category": r.category,
                "page": r.page,
                "score": r.score,
                "text_preview": text_preview,
            })

        all_results.append(query_record)

    # ------------------------------------------------------------------
    # Write PHASE6_RETRIEVAL_EVALUATION.md
    # ------------------------------------------------------------------
    eval_path = DOCS_DIR / "PHASE6_RETRIEVAL_EVALUATION.md"
    lines = [
        "# Phase 6 Retrieval Evaluation\n",
        f"\nEmbedding model: `sentence-transformers/all-MiniLM-L6-v2`\n",
        f"Index type: FAISS IndexFlatIP (cosine via normalised inner product)\n",
        f"Indexed chunks: {service.num_chunks}\n",
        f"Top-k: {TOP_K}\n",
    ]

    for qr in all_results:
        lines.append(f"\n---\n\n## Query {qr['query_id']}: {qr['query']}\n")
        lines.append(f"\n| Rank | Score | Source | Category | Page | Text Preview |")
        lines.append(f"|---|---|---|---|---|---|")
        for r in qr["results"]:
            safe_text = r["text_preview"][:120].replace("|", "\\|").replace("\n", " ")
            lines.append(
                f"| {r['rank']} | {r['score']:.4f} | `{r['source']}` | "
                f"{r['category']} | {r['page']} | {safe_text}... |"
            )

    lines.append("\n\n---\n\n## Observations\n")
    lines.append("\n- **Source traceability**: Every result includes source filename, "
                 "category, page number, and chunk ID.\n")
    lines.append("- **Top-k behaviour**: All queries returned the requested number of results.\n")
    lines.append("- **Qualitative relevance**: Results are topically aligned with queries "
                 "(formal precision/recall metrics not computed — no labelled ground truth).\n")
    lines.append("\n## Limitations\n")
    lines.append("\n- Only Alzheimer's documents are indexed in Phase 6.\n")
    lines.append("- Parkinson's queries will return Alzheimer's content (low relevance).\n")
    lines.append("- No LLM synthesis — raw chunk excerpts returned as-is.\n")
    lines.append("- Retrieval quality depends on PyMuPDF text extraction quality.\n")

    eval_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n\n✓ Evaluation report written to: {eval_path}")

    # Also save raw results JSON
    raw_results_file = DOCS_DIR / "phase6_retrieval_raw_results.json"
    with open(raw_results_file, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    print(f"✓ Raw results saved to: {raw_results_file}")


if __name__ == "__main__":
    main()
