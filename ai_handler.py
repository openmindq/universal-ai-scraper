import requests
import json
import os
import time
import logging
from typing import Dict, Any, Optional
from config import Config
from exceptions import AIHandlerError, RateLimitError

# Log yapılandırması
logger = logging.getLogger(__name__)

def get_prompt_for_task(task_type: str, text: str) -> str:
    prompts: Dict[str, str] = {
        "summary": f"Aşağıdaki web sitesi metnini oku ve şirket/kurum hakkında Türkçe özet oluştur:\n\n{text}",
        "keywords": f"Aşağıdaki metinden en önemli 10 anahtar kelimeyi Türkçe döndür:\n\n{text}",
        "sentiment": f"Aşağıdaki metnin duygu tonunu analiz et:\n\n{text}",
        "tech_stack": f"Aşağıdaki metinden teknoloji yığınını çıkar:\n\n{text}"
    }
    return prompts.get(task_type, prompts["summary"])

def process_with_ai(
    text: str, 
    task_type: str = "summary", 
    model: str = Config.DEFAULT_MODEL, 
    retries: int = Config.RETRY_ATTEMPTS
) -> str:
    api_key = Config.OPENROUTER_API_KEY
    if not api_key:
        raise AIHandlerError("API Key eksik.")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://github.com/openmindq/universal-ai-scraper",
        "X-Title": "Universal Web Scraper AI",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": model,
        "messages": [{"role": "user", "content": get_prompt_for_task(task_type, text)}]
    }
    
    attempt = 0
    while attempt < retries:
        try:
            response = requests.post(Config.OPENROUTER_URL, headers=headers, data=json.dumps(data), timeout=30)
            if response.status_code == 429:
                time.sleep((attempt + 1) * Config.RETRY_DELAY)
                attempt += 1
                continue
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            logger.warning(f"AI hatası: {e}. Deneme {attempt+1}")
            time.sleep(Config.RETRY_DELAY)
            attempt += 1
            
    raise AIHandlerError("AI işlemi başarısız oldu.")
