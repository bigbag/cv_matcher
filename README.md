# CV Matcher

An intelligent system for matching job descriptions with candidate CVs/resumes using advanced text analysis and machine learning algorithms.

## Features

- Parse and analyze CVs in PDF and DOCX formats
- Extract key information from job descriptions
- Smart matching algorithm using ML/AI
- REST API for integration
- Scoring and ranking system
- Candidate management
- Job posting management

## Prerequisites

- Python 3.11+
- PostgreSQL
- Docker (optional)

## Quick Start

1. Clone the repository:
```bash
git clone https://github.com/yourusername/cv_matcher.git
cd cv_matcher
```

2. Set up a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Initialize the database:
```bash
alembic upgrade head
```

6. Run the application:
```bash
uvicorn src.main:app --reload
```

The API will be available at `http://localhost:8000`

## Docker Setup

1. Build the image:
```bash
docker build -t cv_matcher .
```

2. Run the container:
```bash
docker run -p 8000:8000 --env-file .env cv_matcher
```

## API Documentation

Once the application is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Development

1. Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

2. Run tests:
```bash
pytest
```

3. Check code style:
```bash
flake8
black .
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, please open an issue in the GitHub repository or contact the maintainers.

