
# CV Matcher Test Cases Documentation

This document outlines various test cases and usage scenarios for the CV Matcher application. The application provides both CLI and API interfaces for analyzing resumes against job descriptions.

## 1. Getting Started

### 1.1 Installation and Setup

First, create and activate a virtual environment:

```bash
make venv/create
source .venv/bin/activate
```

Install dependencies:
```bash
# Install main dependencies only
make venv/install/main

# Install all dependencies (including test dependencies)
make venv/install/all
```

### 1.2 Running the Service

**Start the Server:**
```bash
make run/server
```

**Using Docker:**
```bash
# Build the Docker image
make docker/build/server

# Run the Docker container
make docker/run/server
```

## 2. CLI Usage

### 2.1 Resume Analysis

**Command:**
```bash
make analyze RESUME_PATH=path/to/resume.pdf JOB_DESC_PATH=path/to/job_description.txt
```

**Expected Output:**
```
Overall Match Score: 75%

Detailed Scoring Criteria:
- Language Proficiency: 80% (Weight: 15%)
- Education Level: 70% (Weight: 20%)
- Experience: 75% (Weight: 25%)
- Technical Skills: 80% (Weight: 25%)
- Certifications: 60% (Weight: 5%)
- Soft Skills: 75% (Weight: 10%)

Match Reasons:
- Strong technical skills alignment
- Relevant industry experience
- Educational background matches requirements
...

Red Flags (if any):
- Missing required certification
- Limited experience in specific area
```

## 3. API Endpoints

### 3.1 Health Check

**Request:**
```http
GET /ping
```

**Expected Response:**
```json
{
    "status": "ok",
    "timestamp": "2024-03-21T10:00:00Z"
}
```

### 3.2 Resume Analysis

**Request:**
```http
POST /analyze_resume
Content-Type: multipart/form-data

Files:
- resume_file: [resume file]
- job_description_file: [job description file]
```

**Expected Response:**
```json
{
    "overall_score": 75,
    "criteria_scores": [
        {
            "name": "Language Proficiency",
            "score": 80,
            "weight": 15,
            "description": "Evaluate candidate's proficiency in required languages"
        },
        {
            "name": "Education Level",
            "score": 70,
            "weight": 20,
            "description": "Evaluate candidate's education level and relevance"
        }
        // ... other criteria
    ],
    "match_reasons": "Detailed explanation of match...",
    "website": "candidate-website.com",
    "red_flags": {
        "low": ["Improvement needed in Soft Skills"],
        "medium": ["Below average Certifications"],
        "high": []
    }
}
```

## 4. Development and Testing

### 4.1 Code Quality

**Run All Tests:**
```bash
make test
```

**Run Linters:**
```bash
# Run all linters
make lint

# Run specific linters
make lint/black
make lint/flake8
make lint/isort
make lint/bandit
make lint/mypy
make lint/yamllint
```

**Format Code:**
```bash
make format
```

### 4.2 Cleanup

**Clean Project:**
```bash
make clean
```

## 5. Scoring Criteria Details

The analysis evaluates candidates based on six main criteria:

1. **Language Proficiency**
   - Required language skills
   - Multilingual abilities
   - Communication proficiency

2. **Education Level**
   - Degree requirements
   - Field of study
   - Academic achievements
   - Alternative education paths

3. **Experience**
   - Years of relevant experience
   - Industry-specific knowledge
   - Project achievements
   - Leadership roles

4. **Technical Skills**
   - Required technical competencies
   - Programming languages
   - Tools and frameworks
   - Industry-specific software

5. **Certifications**
   - Required professional certifications
   - Industry-specific qualifications
   - Validity and recency

6. **Soft Skills**
   - Communication abilities
   - Team collaboration
   - Leadership potential
   - Problem-solving approach

## 6. Supported File Formats

### Resume Files
- PDF (.pdf)
- Word Documents (.doc, .docx)
- Text files (.txt)
- Markdown files (.md)

### Job Description Files
- Text files (.txt)
- Markdown files (.md)
- PDF (.pdf)

## 7. Error Cases and Troubleshooting

### 7.1 Common Errors

1. **File Processing Errors**
   ```
   Error: Could not extract text from resume
   Solution: Ensure the file is not corrupted and in a supported format
   ```

2. **Analysis Errors**
   ```
   Error: Could not extract job requirements
   Solution: Ensure job description is properly formatted and contains clear requirements
   ```

3. **Server Errors**
   ```
   Error: Server connection failed
   Solution: Check if the server is running and accessible
   ```

### 7.2 Troubleshooting Steps

1. **Invalid File Format**
   - Convert file to supported format
   - Check file encoding
   - Ensure file is not password protected

2. **Low Match Score**
   - Review job requirements
   - Update resume format
   - Add missing keywords
   - Include relevant certifications

3. **Server Issues**
   - Check server logs
   - Verify port availability
   - Check network connectivity

## 8. Best Practices

### 8.1 Resume Preparation
- Use standard formats
- Include clear section headers
- List specific technical skills
- Quantify achievements
- Include relevant certifications

### 8.2 Job Description Format
- Clear requirement structure
- Specific technical requirements
- Well-defined qualifications
- Prioritized skills and experience

### 8.3 System Usage
- Keep files under 10MB
- Use text-based formats when possible
- Regular system updates
- Monitor API rate limits

## 9. Limitations

1. **Processing Limits**
   - Maximum file size: 10MB
   - Maximum concurrent requests: Configurable
   - Token limit: 2000 tokens per analysis

2. **Analysis Scope**
   - English language focus
   - Standard resume formats
   - Common industry requirements

3. **Response Time**
   - Typical analysis: 5-15 seconds
   - Timeout: 30 seconds

## 10. Version Control

### 10.1 Generate Changelog
```bash
make sys/changelog
```

### 10.2 Create and Push Tag
```bash
make sys/tag
```

## 11. Help

To see all available commands:
```bash
make help
```

This will display a list of all available commands with their descriptions.
```

This documentation provides a comprehensive guide for using the CV Matcher project, including setup, usage, testing, and troubleshooting. It covers both the CLI and API interfaces, and includes detailed information about the scoring criteria and best practices.
