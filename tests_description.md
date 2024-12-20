# Test Documentation

## Types of Tests

### 1. Unit Tests
Unit tests verify individual components and functions in isolation. The project uses pytest as the testing framework.

Examples:
```python
# Testing entity validation (test_entities.py)
def test_model_config():
    config = ModelConfig(
        model_name="gpt-4",
        api_key="test-key",
        max_tokens=1000,
        temperature=0.7,
    )
    assert config.model_name == "gpt-4"
    assert config.api_key == "test-key"

# Testing utility functions (test_client.py)
@pytest.mark.asyncio
async def test_run_with_string_output(mock_client):
    mock_response = MagicMock()
    mock_response.data = "test response"
    result = await mock_client.run("test prompt", use_cache=False)
    assert result == "test response"

# Testing data validation (test_entities.py)
def test_emphasis_validation():
    with pytest.raises(ValidationError):
        Emphasis(technical_skills_weight=101)  # Over 100
    with pytest.raises(ValidationError):
        Emphasis(soft_skills_weight=-1)  # Under 0

# Testing score parsing (test_analysis.py)
def test_criteria_evaluator_parse_score():
    evaluator = CriteriaEvaluator(mock_client)
    assert evaluator._parse_score("85", "Test") == 85
    assert evaluator._parse_score("Score is 85", "Test") == 85
```

### 2. Integration Tests
Integration tests verify the interaction between different components of the system.

Examples:
```python
# Testing API endpoints (test_routers.py)
@pytest.mark.asyncio
async def test_analyze_resume_success(sample_files, mock_service):
    with open(resume_path, "rb") as resume_file, open(job_desc_path, "rb") as job_desc_file:
        response = client.post(
            "/analyze_resume",
            files={
                "resume_file": ("test_resume.pdf", resume_file, "application/pdf"),
                "job_description_file": ("job_description.txt", job_desc_file, "text/plain"),
            },
        )
    assert response.status_code == 200
    assert result["overall_score"] == 85

# Testing full analysis flow (test_analysis.py)
@pytest.mark.asyncio
async def test_job_analyzer_full_flow(mock_client, sample_resume_text, sample_job_description):
    analyzer = JobAnalyzer(mock_client)
    result = await analyzer.match_resume(
        resume_text=sample_resume_text,
        job_description=sample_job_description,
        job_requirements=job_requirements,
    )
    assert isinstance(result, DetailedMatchResult)
    assert result.overall_score > 0

# Testing cache functionality (test_client.py)
@pytest.mark.asyncio
async def test_cache_functionality(mock_client):
    result1 = await mock_client.run(prompt, system_prompt=system_prompt)
    result2 = await mock_client.run(prompt, system_prompt=system_prompt)
    assert result2 == result1
    assert mock_agent.run.call_count == 1

# Testing service initialization (test_server.py)
def test_app_initialization():
    test_app = init_app()
    assert test_app.title == test_app.title
    assert "/metrics" in [route.path for route in test_app.routes]
```

### 3. API Tests
Tests that verify the REST API endpoints and their responses.

Examples:
```python
# Testing health check endpoint (test_routers.py)
def test_ping_endpoint():
    response = client.get("/ping")
    assert response.status_code == 200
    assert response.json() == {"ping": "pong"}

# Testing file upload validation (test_routers.py)
@pytest.mark.asyncio
async def test_analyze_resume_invalid_file():
    with pytest.raises(FileConversionException):
        client.post(
            "/analyze_resume",
            files={
                "resume_file": ("test.pdf", b"invalid content", "application/pdf"),
                "job_description_file": ("job.txt", b"invalid content", "text/plain"),
            },
        )

# Testing missing file handling (test_routers.py)
@pytest.mark.asyncio
async def test_analyze_resume_missing_file():
    with pytest.raises(RequestValidationError):
        client.post(
            "/analyze_resume",
            files={
                "resume_file": ("test.pdf", b"some content", "application/pdf"),
                # Missing job description file
            },
        )

# Testing metrics endpoint (test_server.py)
def test_metrics_endpoint(client):
    response = client.get("/metrics")
    assert response.status_code == 200
```

### 4. Mock Tests
Tests that use mocking to isolate components and simulate dependencies.

Examples:
```python
# Mocking AI client responses (test_analysis.py)
@pytest.fixture
def mock_client():
    client = MagicMock()
    client.run = AsyncMock()
    return client

# Mocking service responses (test_routers.py)
@pytest.fixture
def mock_service():
    with patch("src.routers.ResumeAnalysisService") as mock:
        service_instance = Mock()
        service_instance.process_files.return_value = ("resume content", "job description content")
        yield service_instance

# Mocking cache directory (test_client.py)
@pytest.fixture
def mock_cache_dir(tmp_path):
    return tmp_path / "cache"

# Mocking settings (test_client.py)
@pytest.fixture
def mock_client(mock_cache_dir):
    with patch("src.client.settings") as mock_settings:
        mock_settings.cache_dir = str(mock_cache_dir)
        mock_settings.anthropic_api_key = "test_key"
        return AIClient(ModelType.ANTHROPIC)
```

## Notable Test Cases

### 1. Resume Analysis Flow
**Description**: Tests the complete resume analysis process from file upload to score generation.
**Contribution**: Ensures the core functionality of matching resumes against job descriptions works correctly.
```python
@pytest.mark.asyncio
async def test_job_analyzer_full_flow(mock_client, sample_resume_text, sample_job_description):
    analyzer = JobAnalyzer(mock_client)
    result = await analyzer.match_resume(
        resume_text=sample_resume_text,
        job_description=sample_job_description,
        job_requirements=job_requirements,
    )
    assert isinstance(result, DetailedMatchResult)
    assert result.overall_score > 0
    assert len(result.criteria_scores) == 6
    assert result.match_reasons == "Match reasons"
```

### 2. Caching System
**Description**: Tests the AI response caching mechanism to optimize performance.
**Contribution**: Verifies that repeated requests use cached responses, reducing API calls and improving response times.
```python
@pytest.mark.asyncio
async def test_cache_functionality(mock_client):
    result1 = await mock_client.run(prompt, system_prompt=system_prompt)
    result2 = await mock_client.run(prompt, system_prompt=system_prompt)
    assert result2 == result1
    assert mock_agent.run.call_count == 1
```

### 3. Score Validation
**Description**: Tests the validation of scoring criteria and weights.
**Contribution**: Ensures that scoring remains within valid ranges and prevents incorrect weight distributions.
```python
def test_emphasis_validation():
    with pytest.raises(ValidationError):
        Emphasis(technical_skills_weight=101)  # Over 100
    with pytest.raises(ValidationError):
        Emphasis(soft_skills_weight=-1)  # Under 0
```

### 4. Error Handling
**Description**: Tests various error scenarios in file processing and API requests.
**Contribution**: Ensures the system gracefully handles invalid inputs and provides appropriate error messages.
```python
@pytest.mark.asyncio
async def test_analyze_resume_invalid_file():
    with pytest.raises(FileConversionException):
        client.post(
            "/analyze_resume",
            files={
                "resume_file": ("test.pdf", b"invalid content", "application/pdf"),
                "job_description_file": ("job.txt", b"invalid content", "text/plain"),
            },
        )
```

## Test Configuration

The project uses the following test configuration:

1. **pytest Configuration**:
```ini
[tool:pytest]
python_files = tests.py test_*.py *_tests.py
addopts = --cov-report=term-missing --cov-config=setup.cfg --cov=src
mock_traceback_monkeypatch = false
```

2. **Coverage Configuration**:
```ini
[coverage:run]
omit = *tests*
```

3. **Test Command**:
```makefile
test:
    LOG_LEVEL=ERROR \
    PYTHONPATH=${PYTHONPATH} \
    $(UV) run \
    $(PYTEST) --disable-warnings $(TEST_DIR) $(PROJECT_PATH) -x -s --cov-report=term-missing --cov-config=setup.cfg --cov=src
``` 