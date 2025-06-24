from pydantic import BaseModel
from typing import List, Optional

class ArticleRequest(BaseModel):
    article_text: str
    title: Optional[str] = None

class EvaluationBreakdown(BaseModel):
    npov_score: int
    verifiability_score: int
    original_research_score: int

class EvaluationResponse(BaseModel):
    overall_score: int
    passes_threshold: bool
    breakdown: EvaluationBreakdown
    feedback: List[str]