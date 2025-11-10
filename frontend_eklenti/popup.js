// Butona tıklama olayını dinle
document.getElementById('analyzeBtn').addEventListener('click', () => {
    // Aktif sekmeyi sorgula
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        const url = tabs[0].url;

        // Sonuç alanını göster ve "Analiz ediliyor..." mesajı koy
        const resultDiv = document.getElementById('result');
        const scoreDiv = document.getElementById('score');
        const decisionDiv = document.getElementById('decision');
        const detailsUl = document.querySelector('#details ul');

        resultDiv.style.display = 'block';
        scoreDiv.textContent = '...';
        decisionDiv.textContent = 'Analiz ediliyor...';
        detailsUl.innerHTML = '';

        // Arka uç API'ye istek gönder
        fetch('http://127.0.0.1:5000/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url: url }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                // Hata durumunda hatayı göster
                decisionDiv.textContent = 'Hata!';
                detailsUl.innerHTML = `<li>${data.error}</li>`;
                scoreDiv.textContent = 'X';
            } else {
                // Başarılı yanıtta sonuçları göster
                scoreDiv.textContent = `${data.guven_puani}`;
                decisionDiv.textContent = `Karar: ${data.karar}`;

                // Analiz dökümünü liste olarak ekle
                if (data.analiz_dokumu && data.analiz_dokumu.length > 0) {
                    data.analiz_dokumu.forEach(item => {
                        const li = document.createElement('li');
                        li.textContent = item;
                        detailsUl.appendChild(li);
                    });
                } else {
                    const li = document.createElement('li');
                    li.textContent = "Herhangi bir risk faktörü bulunamadı.";
                    detailsUl.appendChild(li);
                }

                // Güven puanına göre renklendirme
                if (data.guven_puani < 60) {
                    resultDiv.style.borderColor = '#e74c3c'; // Kırmızı
                } else if (data.guven_puani < 85) {
                    resultDiv.style.borderColor = '#f1c40f'; // Sarı
                } else {
                    resultDiv.style.borderColor = '#2ecc71'; // Yeşil
                }
            }
        })
        .catch(error => {
            // Ağ hatası veya sunucuya ulaşılamama durumunda
            console.error('API isteği sırasında hata:', error);
            resultDiv.style.display = 'block';
            decisionDiv.textContent = 'Hata!';
            scoreDiv.textContent = 'X';
            document.querySelector('#details ul').innerHTML = '<li>Analiz sunucusuna ulaşılamadı. Sunucunun çalıştığından emin olun.</li>';
        });
    });
});
