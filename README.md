# PhishGuard AI - Oltalama Tespit Tarayıcı Uzantısı

PhishGuard AI, kullanıcıları oltalama (phishing) saldırılarından korumak için tasarlanmış akıllı bir tarayıcı uzantısıdır. Ziyaret edilen web sayfalarını gerçek zamanlı olarak analiz eder, bir risk skoru belirler ve kullanıcıyı potansiyel tehditlere karşı uyarır.

## 🎯 Temel Özellikler

-   **Gerçek Zamanlı Analiz**: Web sayfalarını ziyaret edildiği anda, herhangi bir harici veritabanına ihtiyaç duymadan analiz eder.
-   **Kural Tabanlı Puanlama**: URL yapısı, sayfa içeriği, marka taklidi ve sosyal mühendislik taktikleri gibi birden çok kritere dayalı olarak 0-100 arasında bir güven puanı hesaplar.
-   **Anlaşılır Kullanıcı Arayüzü**: Uzantı ikonuna tıklandığında açılan popup penceresi, risk skorunu, analiz özetini ve detaylı dökümü net bir şekilde sunar.
-   **Dinamik İkonlar**: Uzantı ikonu, tespit edilen risk seviyesine göre renk değiştirir (Yeşil, Sarı, Turuncu, Kırmızı), böylece kullanıcı anında görsel bir uyarı alır.

## ⚙️ Nasıl Çalışır?

Uzantı, birkaç bileşenin birlikte çalışmasıyla oltalama tespiti yapar:

1.  **Veri Toplama (`content.js`)**: Kullanıcı bir web sayfasını ziyaret ettiğinde, bu betik sayfaya enjekte edilir. Sayfanın URL'si, başlığı, metin içeriği ve form alanları gibi kritik verileri toplar.
2.  **Arka Plan İşlemleri (`background.js`)**: `content.js` tarafından toplanan veriler, arka planda çalışan bu betiğe gönderilir.
3.  **Analiz Motoru (`analysis.js`)**: `background.js`, aldığı verileri çekirdek analiz motoruna iletir. Bu motor, önceden tanımlanmış kurallara ve ağırlıklara göre verileri işleyerek bir risk skoru hesaplar.
4.  **Sonuçların Depolanması**: Analiz sonucu, ilgili sekmeye özel olarak `chrome.storage.local` üzerinde saklanır.
5.  **Sonuçların Gösterimi (`popup/`)**: Kullanıcı uzantı ikonuna tıkladığında, `popup.js` aktif sekme için saklanan analiz sonucunu okur ve `popup.html` üzerinde görsel olarak sunar.

## 🚀 Kurulum ve Kullanım

Bu uzantıyı test etmek için aşağıdaki adımları izleyebilirsiniz (Chrome ve Chromium tabanlı tarayıcılar için):

1.  Bu repoyu bilgisayarınıza klonlayın veya ZIP olarak indirin.
2.  Tarayıcınızda `chrome://extensions` adresine gidin.
3.  Sağ üst köşedeki **"Geliştirici modu"** (Developer mode) seçeneğini etkinleştirin.
4.  **"Paketlenmemiş öğe yükle"** (Load unpacked) butonuna tıklayın.
5.  İndirdiğiniz proje klasörünü seçin.
6.  Uzantı, tarayıcınızın uzantılar çubuğuna eklenecektir. Herhangi bir web sitesini ziyaret ederek çalışmasını test edebilirsiniz.

## 📁 Dosya Yapısı

```
.
├── manifest.json         # Uzantının yapılandırması ve izinleri
├── background.js         # Arka plan olay yöneticisi (Service Worker)
├── content.js            # Web sayfalarından veri toplayan betik
├── analysis.js           # Çekirdek oltalama analizi motoru
├── popup/
│   ├── popup.html        # Kullanıcı arayüzünün HTML yapısı
│   ├── popup.css         # Kullanıcı arayüzünün stilleri
│   └── popup.js          # Kullanıcı arayüzünün mantığı
└── icons/
    └── ...               # Uzantı ikonları
```

## 🔍 Analiz Kriterleri

Risk skoru hesaplanırken aşağıdaki 5 ana kritere ve ağırlıklarına göre değerlendirme yapılır:

-   **URL ve Domain Analizi (%25)**: Şüpheli anahtar kelimeler, IP adresi kullanımı, HTTPS eksikliği.
-   **İçerik ve Dil Analizi (%30)**: Aciliyet ve korku dili, yazım hataları.
-   **Marka Taklidi Analizi (%20)**: URL ve içerikteki marka tutarsızlığı.
-   **Kullanıcı Girdisi Analizi (%15)**: Hassas bilgi (şifre, kredi kartı) talebi.
-   **Sosyal Mühendislik Analizi (%10)**: Ödül vaadi veya ceza tehdidi.
```