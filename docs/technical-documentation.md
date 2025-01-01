# Technical Documentation

## 1. System Architecture

### Component Overview
The CV Matcher system consists of the following key components:

1. **API Layer** (`src/routers.py`)
   - FastAPI-based REST API endpoints
   - Handles file uploads and request processing
   - Provides health check and resume analysis endpoints

2. **Service Layer** (`src/services.py`)
   - `ResumeAnalysisService`: Core business logic implementation
   - Handles file processing, analysis workflow, and result presentation

3. **Analysis Engine** (`src/analysis.py`)
   - `JobAnalyzer`: Main analysis orchestrator
   - `ResumeProcessor`: Resume text processing
   - `CriteriaEvaluator`: Scoring system implementation
   - `RedFlagAnalyzer`: Identifies potential issues

4. **AI Integration** (`src/client.py`)
   - Abstracted AI model integration
   - Supports multiple AI providers (OpenAI, Anthropic)
   - Implements caching for optimization

### Tech Stack Details

1. **Core Framework**
   - Python 3.9+
   - FastAPI for REST API
   - Uvicorn as ASGI server
   - Pydantic for data validation

2. **Dependencies**
   - `pydantic-ai`: AI model integration
   - `markitdown`: Document text extraction
   - `rich`: Console output formatting
   - `request-id-helper`: Request tracking
   - `python-multipart`: File upload handling
   - `uvloop`: Event loop optimization

3. **Development Tools**
   - pytest for testing
   - black for code formatting
   - flake8 for linting
   - mypy for type checking
   - bandit for security checks

### Integration Approach

1. **AI Model Integration**
   - Abstracted through `AIClientInterface`
   - Supports multiple AI providers
   - Configurable through environment variables
   - Implements response caching

2. **File Processing**
   - Temporary file storage for uploads
   - Secure file handling with cleanup
   - Support for multiple file formats

3. **Error Handling**
   - Comprehensive exception handling
   - Request ID tracking
   - Structured error responses

## 2. Algorithm Design

### Text Processing Methods

1. **Resume Processing**
   - Document text extraction using `markitdown`
   - Format unification through AI processing
   - Website extraction for additional context

2. **Job Description Processing**
   - Structured requirement extraction
   - Keyword identification
   - Weight distribution calculation

### Matching Criteria

1. **Core Evaluation Areas**
   - Technical Skills (50% weight)
   - Soft Skills (20% weight)
   - Experience (20% weight)
   - Education (10% weight)
   - Language Proficiency (5% weight)
   - Certifications (5% weight)

2. **Evaluation Factors**
   - Required vs. optional skills
   - Years of experience
   - Education level
   - Certifications
   - Location requirements

### Scoring System

1. **Score Calculation**
   - Weighted average of individual criteria
   - Score normalization (0-100 scale)
   - Configurable weights through `Emphasis` model

2. **Evaluation Process**
   ```python
   overall_score = sum(criterion.score * criterion.weight for criterion in criteria) // total_weight
   ```

3. **Red Flag Detection**
   - High priority (score < 30, weight >= 30)
   - Medium priority (score < 50, weight >= 20)
   - Low priority (score < 70)

4. **Match Analysis**
   - Detailed scoring breakdown
   - Match reason generation
   - Red flag categorization
   - Visual result presentation
