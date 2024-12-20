# CV Matcher

An intelligent system for matching job descriptions with candidate CVs/resumes using advanced text analysis and machine learning algorithms.

## Features

- Parse and analyze CVs in PDF and DOCX formats
- Extract key information from job descriptions
- Smart matching algorithm using ML/AI
- REST API for integration
- Scoring and ranking system

## Prerequisites

- Python 3.12+
- Docker (optional)

## Quick Start

1. Clone the repository:
```bash
git clone https://github.com/bigbag/cv_matcher.git
cd cv_matcher
```

2. Set up a virtual environment and install dependencies:
```bash
make venv/create
make venv/install/all
```

3. Set up environment variables:
```bash
cp env.example .local_env
# Edit .local_env with your configuration
```

4. Run the application:
```bash
make run/server
```

The API will be available at `http://localhost:8000`

## Using the Analyzer

To analyze a resume against a job description, use the following command:
```bash
make analyze RESUME_PATH=/path/to/resume.pdf JOB_DESC_PATH=/path/to/job.pdf
```

This command will:
- Parse and analyze the provided resume
- Extract requirements from the job description
- Generate a matching score and detailed analysis

## Docker Setup

1. Build the image:
```bash
make docker/build/server
```

2. Run the container:
```bash
make docker/run/server
```

## API Documentation

Once the application is running, visit:
- Swagger UI: `http://localhost:8000/docs`

## Development

1. Format code:
```bash
make format
```

2. Run linters:
```bash
make lint
```

3. Run tests:
```bash
make test
```

4. Clean up temporary files and caches:
```bash
make clean
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, please open an issue in the GitHub repository or contact the maintainers.

