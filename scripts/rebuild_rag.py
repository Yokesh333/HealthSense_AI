"""
scripts/rebuild_rag.py

Rebuilds the FAISS vector store incorporating both Alzheimer's and Parkinson's documents.
Tags each chunk with appropriate disease metadata.
"""

import sys
import logging
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from backend.rag.document_loader import load_documents
from backend.rag.chunker import chunk_documents
from backend.rag.embedder import embed_chunks, save_embeddings
from backend.rag.vector_store import build_index, save_index

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def main():
    logger.info("Starting dual-disease RAG rebuild...")
    
    # 1. Load documents (metadata is assigned in document_loader)
    docs = load_documents()
    if not docs:
        logger.error("No documents loaded. Aborting.")
        sys.exit(1)
        
    alz_docs = sum(1 for d in docs if d.disease == "alzheimers")
    pd_docs = sum(1 for d in docs if d.disease == "parkinsons")
    logger.info(f"Loaded {len(docs)} pages (Alzheimers: {alz_docs}, Parkinsons: {pd_docs})")

    # 2. Chunk documents
    chunks = chunk_documents(docs)
    if not chunks:
        logger.error("No chunks created. Aborting.")
        sys.exit(1)
        
    alz_chunks = sum(1 for c in chunks if c.disease == "alzheimers")
    pd_chunks = sum(1 for c in chunks if c.disease == "parkinsons")
    logger.info(f"Created {len(chunks)} chunks (Alzheimers: {alz_chunks}, Parkinsons: {pd_chunks})")

    # 3. Embed chunks
    embeddings = embed_chunks(chunks)
    
    # Save embeddings to disk
    save_embeddings(embeddings, chunks)
    
    # 4. Build and save vector store
    metadata = [c.model_dump() for c in chunks]
    index = build_index(embeddings, metadata)
    save_index(index, metadata)
    
    logger.info("RAG rebuild complete successfully.")

if __name__ == "__main__":
    main()
