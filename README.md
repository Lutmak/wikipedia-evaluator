# Wikipedia Article Alignment Evaluator

AI-powered tool to evaluate Wikipedia article contributions against core content policies.
this was a quick assesment for casperstudios.xyz

## Setup Instructions

### Prerequisites
- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager
- OpenAI API key

### Installation & Running

**First, install uv (Python package manager):**
```bash
# macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Verify installation:**
```bash
uv --version
```

**Then, set up the project:**
```bash
# Clone repository
git clone <repo-url>
cd wikipedia-evaluator

# Install dependencies with uv
uv sync

# Configure environment
cp .env.example .env
# Edit .env and add your OpenAI API key

# Run API server (Terminal 1)
uv run python app/main.py

# Run Frontend (Terminal 2) 
uv run python frontend/gradio_app.py
```

**Note:** uv automatically manages Python versions - you don't need Python pre-installed.

### Access Points
- **Frontend Interface**: http://localhost:7860
- **API Documentation**: http://localhost:8000/docs  
- **Health Check**: http://localhost:8000/health

## Architecture Overview

```
Frontend (Gradio)     API Layer (FastAPI)     AI Service            External API
┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
│   Simple Web    │──▶│   Async REST    │──▶│  Wikipedia P&G  │──▶│   OpenAI        │
│   Interface     │   │ Validation with │   │  Evaluator with │   │   GPT-4.1-nano  │
│                 │   │  Error Handling │   │  Weighted Score │   │                 │
└─────────────────┘   └─────────────────┘   └─────────────────┘   └─────────────────┘
```

### Core Components
- **FastAPI**: Async REST API with Pydantic validation
- **WikipediaEvaluator**: AI-powered evaluation engine with weighted scoring
- **Gradio Frontend**: Simple web interface with article examples
- **Configuration**: YAML for app settings in 1 place, ENV for secrets and ports for deployment

## Technical Decisions & Rationale

### Model Selection: GPT-4.1-nano
newest fastest and cheaper model, i did a small test script to test response times of OpenAI models
I also used the json mode of the OpenAI API after i got my first JSON format error because begging to the IA to return JSON sometimes isn't reliable enough

### Async Architecture
Used AsyncOpenAI + async FastAPI endpoints because if we didnt used async the response time per request was like 5 to 8 seconds, with these changes we now have average 1.3s response

### Weighted Scoring System
- **NPOV (Neutral Point of View)**: 40% weight (most critical for Wikipedia)
- **Verifiability**: 35% weight (sources are crucial)
- **Original Research**: 25% weight (important but often easier to fix)
- **Rationale**: Based on Wikipedia policy documentation analysis

### Configuration Strategy: 
used 12-Factor App principles since its industry standard and i like to have all the app logic in 1 place
- **YAML**: Business logic that doesn't vary per environment (thresholds, weights)
- **ENV**: Deployment variables that change per environment (API keys, ports)

## Problem Analysis & Solution Approach

### Challenge
Wikipedia needs to balance encouraging new contributors while maintaining content quality standards. Manual review is time-intensive, inconsistent, and creates barriers for new editors unfamiliar with Wikipedia guidelines.

### Solution
I thought of an AI-powered instant evaluation that provides educational feedback aligned with Wikipedia's actual content policies, enabling contributors to learn and improve before submission.

### Core Innovation
Real-time policy evaluation with weighted scoring that prioritizes the most critical Wikipedia guidelines (NPOV > Verifiability > Original Research) while providing specific, actionable improvement suggestions for the user.

## How The Solution Encourages Contributions While Maintaining Quality

### Encouraging Contributions
- **Instant Feedback**: 1-2 second evaluation vs hours/days for human review
- **Educational Guidance**: Specific suggestions help users learn Wikipedia standards


### Maintaining Quality
- **Policy-Based Evaluation**: Assesses against Wikipedia's three core content policies
- **Weighted Scoring**: Critical issues (bias, missing sources) receive higher priority
- **Quality Gate**: 60% threshold prevents fundamentally flawed content progression
- **Consistent Standards**: AI evaluation reduces human reviewer subjectivity

## Implementation Details & Challenges Overcome

i basically vibecode everything here, doing this without AI would have taken me like 3 to 4 days to get to this point, but basically i guided the ideas of the AI to what i would do by myself for this project.

however i faced the following challenges while doing it:


### Challenge 1: API Latency (5 to 8 seconds)
**Problem**: Initial implementation was too slow since i was not using ASYNC, so i added it

### Challenge 2: JSON Parsing Errors
**Problem**: AI responses contained quotes that broke JSON parsing and begging for valid JSON didnt work, so i used the json mode of the Open AI API instead

### Challenge 3: Inconsistent Evaluations
**Problem**: AI evaluation was giving identical scores for different article quality levels, but this was because the prompt was hard coded with those scores so i just made a better prompt

### Challenge 4: Configuration Management
Problem: this wasn't a problem at all but i really think having 1 file to make changes to the parameters of the app really helps with maintainability at any level so i vibe-coded that change and was instant, that way I can properly commit my .env with API keys exposed like a true developer, while keeping the real business logic parameters safely in YAML where they belong.



## Future Improvements

- **Citation Analysis**: Deeper evaluation of source quality and relevance (hierarchical paper evaluation for example)
- **Wikipedia Integration**: Direct editing tool integration via browser extension or using wikipedia API
- **Real-time Collaboration**: Live editing feedback during article creation, like copilot
- **Community Feedback Loop**: Human reviewer validation improves AI accuracy if we want to finetune or own model in the future

---

## Technical Stack
- **Backend**: FastAPI + AsyncOpenAI + Pydantic
- **Frontend**: Gradio + HTTPX
- **AI**: OpenAI GPT-4.1-nano with JSON mode
- **Configuration**: YAML + python-dotenv 
- **Package Management**: uv for fast and better dependency managment and development


