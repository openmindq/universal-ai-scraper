import requests
import logging
from bs4 import BeautifulSoup
from typing import Optional
from config import Config
from exceptions import ScraperError

# Log yapılandırması
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def scrape_url(url: str, timeout: int = Config.SCRAPER_TIMEOUT, max_chars: int = Config.MAX_SCRAPE_CHARS) -> str:
    """
    Belirtilen URL'den sayfa icerigini kazir, gereksiz HTML etiketlerini temizler
    ve belirli bir karakter limitine kadar dondurur.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive"
    }
    
    logger.info(f"URL kazıma başlatıldı: {url}")
    
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'noscript', 'meta']):
            tag.decompose()
            
        text = soup.get_text(separator=' ')
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        logger.info(f"URL başarıyla kazındı. ({len(text)} karakter)")
        return text[:max_chars]
        
    except Exception as e:
        error_msg = f"Kazıma hatası: {str(e)}"
        logger.error(error_msg)
        raise ScraperError(error_msg)

if __name__ == "__main__":
    test_url = "https://example.com"
    try:
        print(scrape_url(test_url)[:500])
    except Exception as e:
        print(e)
