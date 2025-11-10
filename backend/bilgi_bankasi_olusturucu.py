# -*- coding: utf-8 -*-
import json
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image
import imagehash
import io

# Analiz edilecek güvenilir markaların listesi
# Bu liste, projenin ihtiyaçlarına göre genişletilebilir.
TRUSTED_BRANDS = [
    "https://www.google.com",
    "https://www.turkiye.gov.tr",
    "https://www.isbank.com.tr",
    "https://www.garantibbva.com.tr",
    "https://www.twitter.com"
]

# Bilgi bankasının kaydedileceği dosya adı
DB_FILE = "brand_data.json"

def get_favicon_url(driver, url):
    """
    Bir web sitesinin favicon URL'sini bulmaya çalışır.
    Önce <link rel="icon"> etiketini arar, bulamazsa /favicon.ico varsayar.
    """
    try:
        # Standart <link> etiketini bul
        favicon_link = driver.find_element("xpath", "//link[@rel='icon' or @rel='shortcut icon']")
        return favicon_link.get_attribute('href')
    except Exception:
        # Link etiketi yoksa, ana domain'in kökündeki varsayılan yolu dene
        return f"{url.rstrip('/')}/favicon.ico"

def get_image_from_url(url):
    """Verilen bir URL'den bir resim indirir ve PIL Image nesnesi olarak döndürür."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # HTTP 200 olmayan durumlar için hata fırlat
        return Image.open(io.BytesIO(response.content))
    except requests.exceptions.RequestException as e:
        print(f"Hata: Resim indirilemedi ({url}). Sebep: {e}")
        return None

def setup_driver():
    """Selenium WebDriver'ı ayarlar ve başlatır."""
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Tarayıcıyı arayüz olmadan çalıştır
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("window-size=1920x1080")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def main():
    """
    Güvenilir markaların web sitelerini ziyaret ederek
    görsel (favicon, ekran görüntüsü) ve yapısal (renk paleti)
    verilerini toplayan ve bir JSON dosyasına kaydeden ana fonksiyon.
    """
    print("Otonom Bilgi Bankası Oluşturucu başlatılıyor...")
    driver = setup_driver()
    brand_database = []

    for url in TRUSTED_BRANDS:
        print(f"Analiz ediliyor: {url}")
        try:
            driver.get(url)
            time.sleep(5)  # Sayfanın tam olarak yüklenmesi için bekle

            # 1. Favicon Hash'ini Al
            favicon_hash = None
            favicon_url = get_favicon_url(driver, url)
            favicon_image = get_image_from_url(favicon_url)
            if favicon_image:
                favicon_hash = str(imagehash.phash(favicon_image))
                print(f"  -> Favicon hash'i başarıyla oluşturuldu: {favicon_hash}")

            # 2. Ekran Görüntüsü Hash'ini Al
            screenshot_bytes = driver.get_screenshot_as_png()
            screenshot_image = Image.open(io.BytesIO(screenshot_bytes))
            screenshot_hash = str(imagehash.phash(screenshot_image))
            print(f"  -> Ekran görüntüsü hash'i başarıyla oluşturuldu: {screenshot_hash}")

            brand_data = {
                "domain": url.split('//')[1].split('/')[0], # Sadece ana domain'i al (örn: google.com)
                "favicon_url": favicon_url,
                "favicon_hash": favicon_hash,
                "screenshot_hash": screenshot_hash,
            }
            brand_database.append(brand_data)

        except Exception as e:
            print(f"Hata: {url} analiz edilirken bir sorun oluştu. Sebep: {e}")

    # Toplanan verileri JSON dosyasına yaz
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(brand_database, f, indent=4, ensure_ascii=False)

    print(f"\nBilgi bankası başarıyla oluşturuldu ve '{DB_FILE}' dosyasına kaydedildi.")
    driver.quit()

if __name__ == "__main__":
    main()
