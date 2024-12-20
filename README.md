# CV Matcher

A tool for analyzing and matching resumes with job descriptions.

## Overview

CV Matcher is a Python-based application that helps analyze resumes and match them against job descriptions. It provides both CLI and server-based interfaces for resume analysis.

## Requirements

- Python 3.x
- Docker (optional, for containerized deployment)
- Make

## Installation

### Local Setup

1. Create a virtual environment:
```bash
make venv/create
```

2. Install dependencies:
- For main dependencies only:
```bash
make venv/install/main
```
- For all dependencies (including test dependencies):
```bash
make venv/install/all
```

### Docker Setup

1. Build the Docker image:
```bash
make docker/build/server
```

2. Run the container:
```bash
make docker/run/server
```

## Usage

### Analyzing Resume and Job Description

```bash
make analyze RESUME_PATH=/path/to/resume JOB_DESC_PATH=/path/to/job_description
```

### Running the Server

```bash
make run/server
```

## Web API Endpoints

### Health Check
```http
GET /ping
```
Returns a simple health check response to verify the server is running.

### Resume Analysis
```http
POST /analyze_resume
```
Analyze a resume against a job description.

**Request Body (multipart/form-data):**
- `resume_file`: Resume file upload
- `job_description_file`: Job description file upload

**Response:** Detailed match result including:
- Match score
- Analysis details

## Development

### Code Quality

- Run all linters:
```bash
make lint
```

- Format code:
```bash
make format
```

- Run tests:
```bash
make test
```

### Available Linters

- Black (code formatting)
- Flake8 (style guide enforcement)
- isort (import sorting)
- mypy (static type checking)
- yamllint (YAML file linting)

### Cleaning

To clean temporary files and caches:
```bash
make clean
```

### Version Control

- Generate changelog:
```bash
make sys/changelog
```

- Create and push a new tag:
```bash
make sys/tag
```

## Project Structure

```
.
├── src/           # Source code
├── tests/         # Test files
├── examples/      # Example files
├── Dockerfile     # Docker configuration
├── Makefile      # Build and management commands
├── pyproject.toml # Python project configuration
└── setup.cfg      # Setup configuration
```

## License

cv-matcher is developed and distributed under the Apache 2.0 license.
