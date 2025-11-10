# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify
from analiz_motoru import analyze_url
from flask_cors import CORS

# Flask uygulamasını başlat
app = Flask(__name__)
# Frontend'den (tarayıcı eklentisi) gelen isteklere izin vermek için CORS'u etkinleştir
CORS(app)

# --- Risk Puanlama Motoru ---

def calculate_risk_score(analysis_results):
    """
    Analiz sonuçlarını alarak, önceden tanımlanmış sezgisel kurallara göre
    bir tehlike puanı hesaplar ve detaylı bir döküm oluşturur.
    """
    tehlike_puani = 0
    dokum = {
        "gorsel_risk": {"puan": 0, "mesaj": ""},
        "teknik_risk": {"puan": 0, "mesajlar": []},
        "dilsel_risk": {"puan": 0, "mesaj": ""}
    }

    # 1. Görsel Riskler (En Yüksek Ağırlık)
    if analysis_results.get('visual_analysis', {}).get('is_impersonating'):
        puan = 40
        dokum["gorsel_risk"]["puan"] = puan
        marka = analysis_results['visual_analysis']['impersonated_brand']
        dokum["gorsel_risk"]["mesaj"] = f"Yüksek - '{marka}' markası taklit ediliyor olabilir."

    # 2. Teknik Riskler
    teknik_risk_puani = 0

    # Typosquatting
    if analysis_results.get('typosquatting', {}).get('is_typosquatting'):
        teknik_risk_puani += 25
        marka = analysis_results['typosquatting']['closest_brand']
        dokum["teknik_risk"]["mesajlar"].append(f"'{marka}' alan adına benzerlik (Typosquatting)")

    # Alan Adı Yaşı
    domain_yasi = analysis_results.get('domain_age')
    if domain_yasi is not None and domain_yasi < 90:
        teknik_risk_puani += 15
        dokum["teknik_risk"]["mesajlar"].append(f"Alan adı çok yeni ({domain_yasi} günlük)")

    # Şüpheli TLD
    if analysis_results.get('suspicious_tld'):
        teknik_risk_puani += 10
        dokum["teknik_risk"]["mesajlar"].append("Şüpheli TLD uzantısı kullanılıyor")

    # SSL Sertifikası Yokluğu
    if not analysis_results.get('has_ssl'):
        teknik_risk_puani += 5
        dokum["teknik_risk"]["mesajlar"].append("Güvenli bağlantı (HTTPS) kullanılmıyor")

    if teknik_risk_puani > 0:
        dokum["teknik_risk"]["puan"] = teknik_risk_puani

    # 3. Dilsel Riskler
    nlp_sonuclari = analysis_results.get('nlp_analysis', {})
    if nlp_sonuclari.get('keyword_count', 0) > 2:
        puan = 15
        dokum["dilsel_risk"]["puan"] = puan
        kelimeler = nlp_sonuclari['found_keywords']
        dokum["dilsel_risk"]["mesaj"] = f"Orta - Sosyal mühendislik kelimeleri bulundu: {', '.join(kelimeler[:3])}..."

    # Toplam Tehlike Puanını Hesapla
    tehlike_puani = dokum["gorsel_risk"]["puan"] + dokum["teknik_risk"]["puan"] + dokum["dilsel_risk"]["puan"]
    tehlike_puani = min(tehlike_puani, 100)

    # Güven Puanı = 100 - Tehlike Puanı
    guven_puani = 100 - tehlike_puani

    # Nihai Karar
    karar = "Güvenli"
    if tehlike_puani >= 65:
        karar = "Çok Tehlikeli"
    elif tehlike_puani >= 40:
        karar = "Şüpheli"

    # Döküm mesajlarını formatla
    son_dokum = []
    if dokum["gorsel_risk"]["puan"] > 0:
        son_dokum.append(f"Görsel Risk: {dokum['gorsel_risk']['mesaj']} ({dokum['gorsel_risk']['puan']} puan)")
    if dokum["teknik_risk"]["puan"] > 0:
        son_dokum.append(f"Teknik Risk: Orta - Nedenler: {', '.join(dokum['teknik_risk']['mesajlar'])} ({dokum['teknik_risk']['puan']} puan)")
    if dokum["dilsel_risk"]["puan"] > 0:
        son_dokum.append(f"Dilsel Risk: {dokum['dilsel_risk']['mesaj']} ({dokum['dilsel_risk']['puan']} puan)")

    return guven_puani, karar, son_dokum

# --- API Endpoint'i ---

@app.route('/analyze', methods=['POST'])
def analyze():
    """
    İstemciden (tarayıcı eklentisi) bir URL alıp, analiz motorunu çalıştıran
    ve sonuçları standart bir JSON formatında döndüren ana API endpoint'i.
    """
    data = request.json
    if not data or 'url' not in data:
        return jsonify({"error": "Lütfen 'url' parametresini içeren bir JSON gönderin."}), 400

    url_to_analyze = data['url']

    try:
        # Analiz motorunu çağır
        analysis_results = analyze_url(url_to_analyze)

        if "error" in analysis_results:
             return jsonify({"error": analysis_results["error"]}), 400

        # Risk puanını hesapla
        guven_puani, karar, dokum = calculate_risk_score(analysis_results)

        # İstemciye gönderilecek yanıtı formatla
        response = {
            "url": url_to_analyze,
            "guven_puani": guven_puani,
            "karar": karar,
            "analiz_dokumu": dokum
        }

        return jsonify(response)

    except Exception as e:
        print(f"Sunucu hatası: {e}")
        return jsonify({"error": "Analiz sırasında sunucuda beklenmedik bir hata oluştu."}), 500

if __name__ == '__main__':
    # Sunucuyu test amacıyla 0.0.0.0 (tüm arayüzler) ve 5000 portunda çalıştır
    app.run(host='0.0.0.0', port=5000, debug=True)
