import os
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / '.env')
DATA_DIR = Path(os.getenv('DATA_DIR', str(ROOT / 'data'))).resolve()
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / 'projects.sqlite3'
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY','')
GEMINI_MODEL = os.getenv('GEMINI_MODEL','gemini-3.1-pro-preview')
IMAGE_MODEL = os.getenv('IMAGE_MODEL','gemini-3.1-flash-image')
VEO_MODEL = os.getenv('VEO_MODEL','veo-3.1-generate-001')
GOOGLE_CLOUD_PROJECT = os.getenv('GOOGLE_CLOUD_PROJECT','')
VEO_LOCATION = os.getenv('VEO_LOCATION','us-central1')
VEO_GCS_OUTPUT = os.getenv('VEO_GCS_OUTPUT','')
APP_ACCESS_TOKEN = os.getenv('APP_ACCESS_TOKEN','')
PORT = int(os.getenv('PORT', '8000'))
API_TIMEOUT = int(os.getenv('API_TIMEOUT','120'))
VEO_WAIT_SECONDS = int(os.getenv('VEO_WAIT_SECONDS','900'))
VEO_POLL_SECONDS = max(10,int(os.getenv('VEO_POLL_SECONDS','15')))
MAX_RETRIES = int(os.getenv('MAX_RETRIES','3'))
MAX_SOURCE_CHARS = int(os.getenv('MAX_SOURCE_CHARS','45000'))
FFMPEG = os.getenv('FFMPEG','ffmpeg')
FFPROBE = os.getenv('FFPROBE','ffprobe')
