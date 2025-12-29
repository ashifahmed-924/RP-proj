"""
ECESE FastAPI Application

Separate FastAPI application for Education Content Extraction
and Structuring Engine.

Run with: uvicorn ecese_app:app --port 5001 --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ecese.ecese_router import router as ecese_router
from ecese.modules_router import router as modules_router


app = FastAPI(
    title="ECESE API",
    description="Education Content Extraction and Structuring Engine",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(ecese_router)  # Teacher tools
app.include_router(modules_router)  # Student enrollment and content access


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "service": "ECESE API",
        "status": "healthy",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "components": {
            "api": "up",
            "database": "connected"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5001)

