import yaml
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from schemas import ArticleRequest, EvaluationResponse
from evaluator import WikipediaEvaluator

# Load environment variables
load_dotenv()

# Load business logic from YAML
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

app = FastAPI(
    title=config['app']['title'],
    description=config['app']['description'],
    version=config['app']['version']
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure per environment in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize evaluator
evaluator = WikipediaEvaluator()

@app.get("/")
async def root():
    return {
        "message": config['app']['title'],
        "status": "active",
        "version": config['app']['version'],
        "environment": os.getenv("ENVIRONMENT", "development")
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
        "model": config['openai']['model'],
        "quality_threshold": config['evaluation']['quality_threshold'],
        "environment": os.getenv("ENVIRONMENT", "development")
    }

@app.post("/evaluate", response_model=EvaluationResponse)
async def evaluate_article(request: ArticleRequest):
    """
    Evaluate an article against Wikipedia's core guidelines
    
    Returns alignment score and actionable feedback
    """
    
    # Basic validation using config
    if not request.article_text.strip():
        raise HTTPException(status_code=400, detail="Article text cannot be empty")
    
    min_length = config['evaluation']['min_article_length']
    if len(request.article_text) < min_length:
        raise HTTPException(
            status_code=400, 
            detail=f"Article text too short for meaningful evaluation (minimum {min_length} characters)"
        )
    
    max_length = config['evaluation']['max_article_length']
    if len(request.article_text) > max_length:
        raise HTTPException(
            status_code=400, 
            detail=f"Article text too long (max {max_length} characters)"
        )
    
    # Evaluate the article
    try:
        result = await evaluator.evaluate_article(
            article_text=request.article_text,
            title=request.title
        )
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app", 
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", "8000")),
        reload=os.getenv("DEBUG", "false").lower() == "true"
    )