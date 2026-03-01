import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Proje yapılandırma ayarlarını yöneten sınıf."""
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
    DEFAULT_MODEL = "google/gemma-7b-it:free"
    SCRAPER_TIMEOUT = 15
    MAX_SCRAPE_CHARS = 4000
    RETRY_ATTEMPTS = 3
    RETRY_DELAY = 2
    
    @classmethod
    def validate(cls) -> bool:
        """Kritik yapılandırma ayarlarının varlığını kontrol eder."""
        if not cls.OPENROUTER_API_KEY:
            return False
        return True
