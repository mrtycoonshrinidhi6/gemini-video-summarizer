import os
from dotenv import load_dotenv
from pathlib import Path
import yaml

# Load environment variables
load_dotenv()

class Config:
    """Central configuration class for the video summarization system"""

    # --- Gemini AI Configuration ---
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')
    GEMINI_SAFETY_SETTINGS = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"}
    ]

    # --- Video Processing ---
    FRAME_EXTRACTION_RATE = float(os.getenv('FRAME_EXTRACTION_RATE', 1))
    KEYFRAME_THRESHOLD = float(os.getenv('KEYFRAME_THRESHOLD', 0.5))
    MAX_FRAME_DIMENSION = int(os.getenv('MAX_FRAME_DIMENSION', 1024))

    # --- Audio Processing ---
    AUDIO_EXTRACTION_ENABLED = bool(int(os.getenv('AUDIO_EXTRACTION_ENABLED', 1)))
    AUDIO_SAMPLE_RATE = int(os.getenv('AUDIO_SAMPLE_RATE', 16000))  # Whisper compatible
    AUDIO_MODEL = os.getenv('AUDIO_MODEL', 'gemini-2.5-flash')  # or "" whisper-large-v3
    AUDIO_LANGUAGE = os.getenv('AUDIO_LANGUAGE', 'en')

    # --- Path Configuration ---
    PROJECT_ROOT = Path(__file__).parent.parent

    KEYFRAMES_DIR = PROJECT_ROOT / 'outputs' / 'keyframes'
    SUMMARIES_DIR = PROJECT_ROOT / 'outputs' / 'summaries'
    AUDIO_DIR = PROJECT_ROOT / 'outputs' / 'audio'

    FRONTEND_KEYFRAMES_DIR = PROJECT_ROOT / 'frontend' / 'temp_outputs' / 'keyframes'
    FRONTEND_SUMMARIES_DIR = PROJECT_ROOT / 'frontend' / 'temp_outputs' / 'summaries'
    FRONTEND_AUDIO_DIR = PROJECT_ROOT / 'frontend' / 'temp_outputs' / 'audio'
    FRONTEND_UPLOADS_DIR = PROJECT_ROOT / 'frontend' / 'temp_uploads'

    TEMP_DIR = PROJECT_ROOT / 'temp'

    # --- Cloud Configuration ---
    CLOUD_CONFIG_PATH = PROJECT_ROOT / 'config' / 'cloud_config.yaml'

    @classmethod
    def load_cloud_config(cls):
        if cls.CLOUD_CONFIG_PATH.exists():
            with open(cls.CLOUD_CONFIG_PATH, 'r') as f:
                return yaml.safe_load(f)
        return {}

    @classmethod
    def ensure_directories(cls):
        """Create required directories if they don't exist"""
        dirs = [
            cls.KEYFRAMES_DIR, cls.SUMMARIES_DIR, cls.AUDIO_DIR, cls.TEMP_DIR,
            cls.FRONTEND_KEYFRAMES_DIR, cls.FRONTEND_SUMMARIES_DIR,
            cls.FRONTEND_AUDIO_DIR, cls.FRONTEND_UPLOADS_DIR
        ]
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)

# Initialize directories on import
Config.ensure_directories()
