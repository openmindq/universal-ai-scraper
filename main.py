import scraper
import ai_handler
import argparse
import logging
import sys
from config import Config
from exceptions import ScraperError, AIHandlerError

# Log yapılandırması
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("main")

def parse_args() -> argparse.Namespace:
    """Komut satırı argümanlarını ayrıştırır."""
    parser = argparse.ArgumentParser(description="Herhangi bir web sitesini kazıyarak AI ile içerik analizi yapan genel amaçlı araç.")
    parser.add_argument(
        "--url", 
        type=str, 
        required=True,
        help="Kazınacak ve analiz edilecek hedef web sitesi URL'si."
    )
    parser.add_argument(
        "--task", 
        type=str, 
        choices=["summary", "keywords", "sentiment", "tech_stack"], 
        default="summary",
        help="Yapay zeka tarafından yapılacak analiz türü."
    )
    parser.add_argument(
        "--model", 
        type=str, 
        default=Config.DEFAULT_MODEL,
        help=f"Kullanılacak OpenRouter AI model adı (Varsayılan: {Config.DEFAULT_MODEL})."
    )
    parser.add_argument(
        "--output", 
        type=str, 
        default="",
        help="Çıktının kaydedileceği dosya yolu (opsiyonel). Örn: sonuc.txt"
    )
    return parser.parse_args()

def run_pipeline(args: argparse.Namespace) -> None:
    """Kazıma ve AI işleme sürecini yönetir."""
    
    if not Config.validate():
        logger.error("HATA: OPENROUTER_API_KEY eksik. Lütfen .env dosyasını kontrol edin.")
        sys.exit(1)

    try:
        # 1. Aşama: Kazıma
        logger.info(f"Süreç başlatıldı. Hedef: {args.url}")
        raw_text = scraper.scrape_url(args.url)
        
        # 2. Aşama: AI İşleme
        logger.info(f"AI Analizi başlatılıyor. Görev: {args.task}")
        result = ai_handler.process_with_ai(
            text=raw_text, 
            task_type=args.task, 
            model=args.model
        )
        
        # 3. Sonuçları Görüntüle
        print("\n" + "="*60)
        print(f"ANALİZ SONUCU ({args.url.upper()} - {args.task.upper()})")
        print("="*60)
        print(result)
        print("="*60 + "\n")
        
        # 4. Dosyaya Kaydet (Opsiyonel)
        if args.output:
            try:
                with open(args.output, "w", encoding="utf-8") as f:
                    f.write(f"URL: {args.url}\n")
                    f.write(f"GÖREV: {args.task}\n")
                    f.write(f"MODEL: {args.model}\n")
                    f.write("="*40 + "\n")
                    f.write(result + "\n")
                logger.info(f"Sonuç başarıyla '{args.output}' dosyasına kaydedildi.")
            except Exception as e:
                logger.error(f"Çıktı dosyaya yazılamadı: {e}")

    except ScraperError as e:
        logger.error(f"Kazıma aşamasında hata: {e}")
    except AIHandlerError as e:
        logger.error(f"AI işleme aşamasında hata: {e}")
    except KeyboardInterrupt:
        logger.info("\nİşlem kullanıcı tarafından durduruldu.")
    except Exception as e:
        logger.critical(f"Beklenmeyen kritik hata: {e}")

if __name__ == "__main__":
    args = parse_args()
    run_pipeline(args)
