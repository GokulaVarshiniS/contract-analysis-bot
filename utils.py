# src/utils.py

import os
import json
import hashlib
from datetime import datetime
from typing import Dict, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_file_hash(file_path: str) -> str:
    """Generate MD5 hash of file for tracking"""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def sanitize_text(text: str) -> str:
    """Sanitize text for safe processing"""
    # Remove null bytes
    text = text.replace('\x00', '')
    # Remove control characters
    text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\r\t')
    return text


def format_currency(amount: float, currency: str = "INR") -> str:
    """Format currency for display"""
    if currency == "INR":
        return f"₹{amount:,.2f}"
    return f"{currency} {amount:,.2f}"


def truncate_text(text: str, max_length: int = 500) -> str:
    """Truncate text with ellipsis"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."


def save_json(data: Dict, filepath: str) -> bool:
    """Save dictionary to JSON file"""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"Error saving JSON: {e}")
        return False


def load_json(filepath: str) -> Dict:
    """Load JSON file to dictionary"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading JSON: {e}")
        return {}


def ensure_directories():
    """Ensure all required directories exist"""
    directories = ['uploads', 'exports', 'audit_logs', 'templates']
    for dir_name in directories:
        os.makedirs(dir_name, exist_ok=True)


def get_timestamp() -> str:
    """Get formatted timestamp"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def calculate_reading_time(text: str) -> int:
    """Calculate estimated reading time in minutes"""
    words = len(text.split())
    return max(1, words // 200)  # Assuming 200 words per minute


class Config:
    """Application configuration"""
    
    # API Settings
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    
    # File Settings
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
    ALLOWED_EXTENSIONS = ['.pdf', '.docx', '.doc', '.txt']
    
    # Analysis Settings
    MAX_CLAUSES_TO_ANALYZE = 20
    MAX_TEXT_LENGTH = 50000
    
    # Output Settings
    EXPORT_DIR = "exports"
    AUDIT_DIR = "audit_logs"
    TEMPLATE_DIR = "templates"
    
    @classmethod
    def validate(cls) -> bool:
        """Validate configuration"""
        if not cls.ANTHROPIC_API_KEY and not cls.OPENAI_API_KEY:
            logger.warning("No API keys configured")
            return False
        return True