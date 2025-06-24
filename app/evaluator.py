import json
import yaml
import os
from openai import AsyncOpenAI
from schemas import EvaluationResponse, EvaluationBreakdown

# Load business logic from YAML
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

class WikipediaEvaluator:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.threshold = config['evaluation']['quality_threshold']
        self.max_article_length = config['evaluation']['max_article_length']
        self.weights = config['evaluation']['weights']
    
    async def evaluate_article(self, article_text: str, title: str = None) -> EvaluationResponse:
        """Evaluate article against Wikipedia's core content policies"""
        
        # Enhanced input validation
        if len(article_text) > self.max_article_length:
            return self._fallback_response(
                f"Article too long ({len(article_text)} chars). Maximum allowed: {self.max_article_length} characters."
            )
        
        # Check for potential encoding issues
        try:
            article_text.encode('utf-8')
        except UnicodeEncodeError:
            return self._fallback_response("Article contains invalid characters. Please use UTF-8 encoded text.")
        
        prompt = self._build_enhanced_evaluation_prompt(article_text, title)
        
        try:
            response = await self.client.chat.completions.create(
                model=config['openai']['model'],
                messages=[
                    {"role": "system", "content": "You are an expert Wikipedia editor who evaluates articles against Wikipedia's core content policies. You must respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=config['openai']['temperature']
            )
            
            response_text = response.choices[0].message.content.strip()
            result = json.loads(response_text)
            
            # Validate response structure
            if not self._validate_response_structure(result):
                return self._fallback_response("Invalid evaluation response format.")
            
            # Calculate weighted overall score
            weighted_score = (
                result["breakdown"]["npov_score"] * self.weights["npov_score"] +
                result["breakdown"]["verifiability_score"] * self.weights["verifiability_score"] + 
                result["breakdown"]["original_research_score"] * self.weights["original_research_score"]
            )
            
            return EvaluationResponse(
                overall_score=int(round(weighted_score)),
                passes_threshold=weighted_score >= self.threshold,
                breakdown=EvaluationBreakdown(**result["breakdown"]),
                feedback=result.get("feedback", ["No specific feedback provided."])
            )
            
        except json.JSONDecodeError:
            return self._fallback_response("Unable to parse evaluation response. Please try again.")
            
        except Exception as e:
            # Log error in production environment
            error_msg = "Evaluation service temporarily unavailable. Please try again in a moment."
            if os.getenv("DEBUG", "false").lower() == "true":
                error_msg += f" (Debug: {str(e)})"
            return self._fallback_response(error_msg)

    def _validate_response_structure(self, result: dict) -> bool:
        """Validate that the response has the expected structure"""
        try:
            breakdown = result.get("breakdown", {})
            required_scores = ["npov_score", "verifiability_score", "original_research_score"]
            
            for score_key in required_scores:
                score = breakdown.get(score_key)
                if not isinstance(score, (int, float)) or score < 0 or score > 100:
                    return False
            
            feedback = result.get("feedback", [])
            if not isinstance(feedback, list):
                return False
                
            return True
        except Exception:
            return False

    def _build_enhanced_evaluation_prompt(self, article_text: str, title: str = None) -> str:
        """Enhanced prompt based on Wikipedia's actual policies"""
        
        title_part = f"Title: {title}\n\n" if title else ""
        
        return f"""
Evaluate this Wikipedia article draft against Wikipedia's three core content policies. 

{title_part}Article Text:
{article_text}

**EVALUATION CRITERIA:**

**1. NEUTRAL POINT OF VIEW (NPOV) - Score 0-100:**
- Does it avoid stating opinions as facts?
- Are viewpoints presented proportionally to their prominence in reliable sources?
- Is promotional, biased, or editorial language avoided?
- Are controversial topics presented fairly without taking sides?
- RED FLAGS: promotional language, personal opinions stated as fact

**2. VERIFIABILITY - Score 0-100:**  
- Are factual claims supported or supportable by reliable sources?
- Would readers be able to verify the information?
- Are there inline citations where needed?
- Do claims avoid being challenged or likely to be challenged without sources?
- RED FLAGS: Unsourced statistics, unattributed quotes, unverifiable claims

**3. NO ORIGINAL RESEARCH - Score 0-100:**
- Is content based on published sources rather than editor analysis?
- Are there novel theories, personal interpretations, or synthesis?
- Does it avoid reaching conclusions not stated in sources?
- RED FLAGS: Personal experiences, novel connections between ideas, unpublished analysis

**SCORING GUIDELINES:**
- 90-100: Excellent, minor improvements only
- 70-89: Good, some improvements needed  
- 50-69: Significant issues, substantial revision required
- 30-49: Major problems, extensive rewriting needed
- 0-29: Fundamental violations, complete overhaul required

**IMPORTANT: Use only plain text in feedback without quotes, apostrophes, or special characters.**

Return ONLY this JSON format with no additional text:
{{
  "breakdown": {{
    "npov_score": [number],
    "verifiability_score": [number], 
    "original_research_score": [number]
  }},
  "feedback": [
    "CRITICAL: [issue without quotes]",
    "IMPROVE: [suggestion without quotes]",
    "MINOR: [enhancement without quotes]"
  ]
}}

Analyze the SPECIFIC content and give appropriate scores based on actual policy violations found.
"""

    def _fallback_response(self, error_msg: str) -> EvaluationResponse:
        """Fallback response for errors"""
        return EvaluationResponse(
            overall_score=0,
            passes_threshold=False,
            breakdown=EvaluationBreakdown(
                npov_score=0,
                verifiability_score=0,
                original_research_score=0
            ),
            feedback=[error_msg]
        )