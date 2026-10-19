import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI

from backend.api.adni import router as adni_router
from backend.api.parkinson import router as parkinson_router
from backend.api.agents import router as agents_router
from backend.api.rag import router as rag_router
from backend.api.questionnaire import router as questionnaire_router
from backend.api.reports import router as reports_router
from backend.services.adni_predictor import ADNIPredictor
from backend.services.parkinson_predictor import ParkinsonPredictor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    import time
    startup_start = time.time()
    logger.info("Starting up HealthSense AI Backend...")

    # ADNI Model
    try:
        t0 = time.time()
        logger.info("[STARTUP] Loading ADNI model...")
        adni_predictor = ADNIPredictor()
        adni_predictor.load_model()
        app.state.adni_predictor = adni_predictor
        logger.info(f"[STARTUP] ADNI model loaded in {time.time() - t0:.2f}s.")
    except Exception as e:
        app.state.adni_predictor = None
        logger.error(f"Failed to load ADNI Predictor: {e}")

    # Parkinson Model
    try:
        t0 = time.time()
        logger.info("[STARTUP] Loading Parkinson model...")
        parkinson_predictor = ParkinsonPredictor()
        parkinson_predictor.load_model()
        app.state.parkinson_predictor = parkinson_predictor
        logger.info(f"[STARTUP] Parkinson model loaded in {time.time() - t0:.2f}s.")
    except Exception as e:
        app.state.parkinson_predictor = None
        logger.error(f"Failed to load Parkinson Predictor: {e}")
    
    # RAG Service
    try:
        t0 = time.time()
        logger.info("[STARTUP] Loading RAG index & embedding model...")
        from backend.rag.service import RAGService
        from backend.rag.vector_store import vector_store_exists
        if vector_store_exists():
            rag_service = RAGService()
            app.state.rag_service = rag_service
            logger.info(f"[STARTUP] RAG Service loaded in {time.time() - t0:.2f}s — {rag_service.num_chunks} chunks indexed.")
        else:
            app.state.rag_service = None
            logger.warning("RAG knowledge base not built yet. Run the ingestion pipeline first.")
    except Exception as e:
        app.state.rag_service = None
        logger.error(f"Failed to load RAG Service: {e}")
        
    # Web Intelligence Service
    try:
        t0 = time.time()
        logger.info("[STARTUP] Initializing PubMed Web Intelligence...")
        from backend.services.web_intelligence_service import PubMedWebIntelligenceService
        app.state.web_service = PubMedWebIntelligenceService()
        logger.info(f"[STARTUP] PubMed Web Intelligence initialized in {time.time() - t0:.2f}s.")
    except Exception as e:
        app.state.web_service = None
        logger.error(f"Failed to load Web Intelligence Service: {e}")
    
    # LLM Service
    try:
        t0 = time.time()
        logger.info("[STARTUP] Initializing Groq LLM Service...")
        from backend.config import GROQ_API_KEY
        if GROQ_API_KEY:
            from backend.services.llm_service import GroqLLMService
            app.state.llm_service = GroqLLMService()
            logger.info(f"[STARTUP] Groq LLM Service initialized in {time.time() - t0:.2f}s.")
        else:
            app.state.llm_service = None
            logger.info("GROQ_API_KEY not found. LLM Service will be unavailable.")
    except Exception as e:
        app.state.llm_service = None
        logger.error(f"Failed to load LLM Service: {e}")
    
    logger.info(f"[STARTUP] Total HealthSense AI startup completed in {time.time() - startup_start:.2f}s.")
    yield
    
    # Shutdown
    logger.info("Shutting down HealthSense AI Backend...")
    app.state.adni_predictor = None
    app.state.parkinson_predictor = None
    app.state.rag_service = None

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="HealthSense AI", 
    description="Backend API for HealthSense AI", 
    version="0.1.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(adni_router, prefix="/api/adni", tags=["ADNI Prediction"])
app.include_router(parkinson_router, prefix="/api/parkinson", tags=["Parkinson Prediction"])
app.include_router(agents_router, prefix="/api/agents", tags=["Multi-Agent"])
app.include_router(rag_router, prefix="/api/rag", tags=["Biomedical RAG"])
app.include_router(questionnaire_router)
app.include_router(reports_router)

@app.get("/")
def read_root():
    return {"message": "Welcome to HealthSense AI API!"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
