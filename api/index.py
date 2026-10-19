import sys
from pathlib import Path

# Add project root to sys.path so 'src' imports resolve in Vercel Serverless environment
sys.path.append(str(Path(__file__).parent.parent))

from src.main import app
