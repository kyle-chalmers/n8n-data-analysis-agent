"""FastAPI application for Production Line Health Advisor."""
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uuid
import logging

from models.schemas import AnalysisResponse, ChatRequest, ChatResponse, HealthResponse
from analysis.data_loader import load_csv_from_bytes, validate_production_data, get_summary_stats
from agent.core import agent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Production Line Health Advisor",
    description="AI-powered analysis agent for manufacturing data. Uses Ollama (local LLM) - no API keys needed!",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    ollama_ok = agent.check_ollama_connection()
    return HealthResponse(
        status="healthy",
        ollama_status="connected" if ollama_ok else "disconnected"
    )


@app.post("/webhook/analyze", response_model=AnalysisResponse)
async def analyze_csv(file: UploadFile = File(...)):
    """
    Analyze an uploaded CSV file.

    Upload a production/manufacturing CSV and get an AI-powered health report
    with visualizations and actionable insights.
    """
    logger.info(f"Received file: {file.filename}")

    # Validate file type
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files accepted")

    try:
        # Read and parse CSV
        contents = await file.read()
        df = load_csv_from_bytes(contents)
        logger.info(f"Loaded CSV with {len(df)} rows, {len(df.columns)} columns")

        # Validate schema (warning only)
        valid, message = validate_production_data(df)
        if not valid:
            logger.warning(f"Schema validation warning: {message}")

        # Create session and load data
        session_id = str(uuid.uuid4())
        agent.load_data(session_id, df)
        logger.info(f"Created session: {session_id}")

        # Run initial analysis
        result = agent.run_initial_analysis(session_id)

        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])

        # Get summary stats
        stats = get_summary_stats(df)

        return AnalysisResponse(
            session_id=session_id,
            summary=result.get("response", "Analysis complete"),
            insights=[],  # Could parse from response if needed
            charts=result.get("charts", []),
            raw_stats=stats
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/webhook/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat with the agent about previously uploaded data.

    Ask follow-up questions about your production data. The agent remembers
    the context from your uploaded CSV.
    """
    logger.info(f"Chat request for session: {request.session_id}")

    try:
        result = agent.chat(request.session_id, request.message)

        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])

        return ChatResponse(
            session_id=request.session_id,
            response=result.get("response", ""),
            charts=result.get("charts")
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
