# -*- coding: utf-8 -*-
import whois
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from Levenshtein import distance as levenshtein_distance
from urllib.parse import urlparse
import json
import imagehash
from PIL import Image
import io
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

# --- Konfigürasyon ve Sabitler ---

# Bilgi bankası dosyasının yolu
DB_FILE = "brand_data.json"

# Spamhaus Project gibi kaynaklara dayalı şüpheli TLD'lerin listesi
SUSPICIOUS_TLDS = [
    '.xyz', '.top', '.live', '.buzz', '.info', '.club', '.online', '.site', '.website',
    '.shop', '.icu', '.gq', '.ml', '.cf', '.tk', '.ga', '.work'
]

# Sosyal mühendislik ve aciliyet belirten anahtar kelimeler
NLP_KEYWORDS = [
    "acil", "hemen", "şimdi", "giriş yap", "doğrula", "onayla", "askıya alındı",
    "hesabınız", "kısıtlandı", "ödül", "kazandınız", "tebrikler", "bedava",
    "promosyon", "teklif", "sınırlı", "son şans", "güvenlik uyarısı", "şifre"
]

# --- Yardımcı Fonksiyonlar ---

def load_brand_data():
    """brand_data.json dosyasını yükler ve içeriğini döndürür."""
    try:
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Hata: Bilgi bankası dosyası ({DB_FILE}) bulunamadı.")
        return []

def get_domain_from_url(url):
    """Verilen bir URL'den ana domain'i (örn: google.com) çıkarır."""
    try:
        return urlparse(url).netloc.replace('www.', '')
    except Exception:
        return None

# --- 1. Teknik Analiz Katmanı ---

def get_domain_age_days(domain):
    """Bir alan adının yaşını gün olarak hesaplar."""
    try:
        w = whois.whois(domain)
        creation_date = w.creation_date
        if isinstance(creation_date, list):
            creation_date = creation_date[0]
        if creation_date:
            return (datetime.now() - creation_date).days
    except Exception:
        return None  # WHOIS bilgisi alınamazsa

def check_tld(domain):
    """URL'nin TLD'sinin şüpheli listesinde olup olmadığını kontrol eder."""
    tld = '.' + domain.split('.')[-1]
    return tld in SUSPICIOUS_TLDS

def check_ssl(url):
    """URL'nin HTTPS kullanıp kullanmadığını kontrol eder."""
    return url.startswith('https://')

def check_typosquatting(domain, brand_data):
    """
    Verilen domain'in, bilgi bankasındaki güvenilir domain'lere
    Levenshtein mesafesini hesaplayarak typosquatting riskini ölçer.
    """
    min_distance = float('inf')
    closest_brand = None
    for brand in brand_data:
        dist = levenshtein_distance(domain, brand['domain'])
        if dist < min_distance:
            min_distance = dist
            closest_brand = brand['domain']

    # Eğer en yakın markaya olan mesafe 1 veya 2 ise, bu yüksek bir risktir.
    if 0 < min_distance <= 2:
        return {"is_typosquatting": True, "closest_brand": closest_brand, "distance": min_distance}
    return {"is_typosquatting": False}

# --- 2. Dilsel Analiz Katmanı (NLP) ---

def analyze_text_content(url):
    """
    Bir web sitesinin metin içeriğini çeker ve şüpheli anahtar kelimeleri arar.
    """
    try:
        response = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Sayfadaki tüm görünür metinleri al
        for script in soup(["script", "style"]):
            script.extract()
        text = soup.get_text().lower()

        found_keywords = [keyword for keyword in NLP_KEYWORDS if keyword in text]
        return {"keyword_count": len(found_keywords), "found_keywords": list(set(found_keywords))}
    except requests.exceptions.RequestException:
        return {"keyword_count": 0, "found_keywords": []}

# --- 3. Görsel Analiz Katmanı ---

def get_favicon_hash_from_url(url, driver):
    """Bir URL'nin favicon'unu indirir ve phash'ini hesaplar."""
    try:
        # Favicon URL'sini bulmak için JavaScript kullan
        favicon_url = driver.execute_script("""
            let link = document.querySelector("link[rel~='icon']");
            if (link) return link.href;
            return window.location.origin + '/favicon.ico';
        """)

        response = requests.get(favicon_url, timeout=10)
        response.raise_for_status()
        image = Image.open(io.BytesIO(response.content))
        return str(imagehash.phash(image))
    except Exception:
        return None

def get_screenshot_hash(driver):
    """Mevcut sayfanın ekran görüntüsünü alır ve phash'ini hesaplar."""
    try:
        screenshot_bytes = driver.get_screenshot_as_png()
        image = Image.open(io.BytesIO(screenshot_bytes))
        return str(imagehash.phash(image))
    except Exception:
        return None

def check_visual_similarity(favicon_hash, screenshot_hash, brand_data):
    """
    Analiz edilen sitenin görsel hash'lerini, bilgi bankasındaki
    referans hash'ler ile karşılaştırır.
    """
    # Hash'ler arasındaki maksimum kabul edilebilir Hamming mesafesi.
    # Bu değer ne kadar düşükse, o kadar katı bir eşleşme aranır.
    HASH_THRESHOLD = 5

    impersonated_brand = None

    for brand in brand_data:
        # Favicon hash karşılaştırması
        if brand["favicon_hash"] and favicon_hash:
            dist = imagehash.hex_to_hash(brand["favicon_hash"]) - imagehash.hex_to_hash(favicon_hash)
            if dist <= HASH_THRESHOLD:
                impersonated_brand = brand["domain"]
                break # Eşleşme bulundu, döngüden çık

        # Ekran görüntüsü hash karşılaştırması
        if brand["screenshot_hash"] and screenshot_hash:
            dist = imagehash.hex_to_hash(brand["screenshot_hash"]) - imagehash.hex_to_hash(screenshot_hash)
            if dist <= HASH_THRESHOLD:
                impersonated_brand = brand["domain"]
                break

    if impersonated_brand:
        return {"is_impersonating": True, "impersonated_brand": impersonated_brand}
    return {"is_impersonating": False}

# --- Ana Analiz Fonksiyonu ---

def analyze_url(url):
    """
    Verilen bir URL'yi 3 katmanda analiz eder ve sonuçları bir
    sözlük olarak döndürür.
    """
    print(f"Analiz başlatılıyor: {url}")
    results = {}
    domain = get_domain_from_url(url)
    if not domain:
        return {"error": "Geçersiz URL"}

    brand_data = load_brand_data()

    # Teknik Analiz
    results['domain_age'] = get_domain_age_days(domain)
    results['suspicious_tld'] = check_tld(domain)
    results['has_ssl'] = check_ssl(url)
    results['typosquatting'] = check_typosquatting(domain, brand_data)

    # Dilsel Analiz
    results['nlp_analysis'] = analyze_text_content(url)

    # Görsel Analiz (Selenium gerektirir)
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("window-size=1920x1080")

    driver = None
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get(url)
        time.sleep(3) # Sayfanın render olması için bekle

        favicon_hash = get_favicon_hash_from_url(url, driver)
        screenshot_hash = get_screenshot_hash(driver)

        results['visual_analysis'] = check_visual_similarity(favicon_hash, screenshot_hash, brand_data)

    except Exception as e:
        print(f"Görsel analiz sırasında hata: {e}")
        results['visual_analysis'] = {"error": "Görsel analiz tamamlanamadı."}
    finally:
        if driver:
            driver.quit()

    print("Analiz tamamlandı.")
    return results

if __name__ == '__main__':
    # Bu modül doğrudan çalıştırıldığında test amaçlı bir analiz yapar.
    test_url = "http://example.com" # Test için güvenli bir URL
    analysis_result = analyze_url(test_url)
    print(json.dumps(analysis_result, indent=4))
