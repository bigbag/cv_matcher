import sys
from pathlib import Path

# Add the src directory to Python path for imports
src_path = str(Path(__file__).parent.parent)
if src_path not in sys.path:
    sys.path.append(src_path)

# Configure pytest-asyncio as the default async backend
pytest_plugins = ("pytest_asyncio",)
