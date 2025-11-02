/**
 * PhishGuard AI - Core Analysis Engine
 * This script contains the logic for analyzing web page data to detect phishing attempts.
 */

// Main function to analyze the page data
function analyzePage(data) {
    const { url, page_title, visible_text, input_fields, brand_indicators } = data;

    // 1. Perform analysis for each category
    const urlAnalysis = analyzeUrl(url);
    const contentAnalysis = analyzeContent(visible_text, page_title);
    const brandAnalysis = analyzeBrand(brand_indicators, url);
    const inputAnalysis = analyzeInputs(input_fields);
    const socialEngineeringAnalysis = analyzeSocialEngineering(visible_text);

    // 2. Calculate the weighted risk score
    const riskScore = Math.round(
        (urlAnalysis.score * 0.25) +
        (contentAnalysis.score * 0.30) +
        (brandAnalysis.score * 0.20) +
        (inputAnalysis.score * 0.15) +
        (socialEngineeringAnalysis.score * 0.10)
    );

    // 3. Determine the verdict and recommendation
    let verdict = "DÜŞÜK RİSK";
    let recommendation = "Bu site muhtemelen güvenli. Yine de dikkatli olun.";
    if (riskScore > 85) {
        verdict = "KRİTİK RİSK - YÜKSEK OLASILIKLA OLTALAMA";
        recommendation = "Bu siteden derhal çıkın! Asla kişisel bilgilerinizi girmeyin ve siteyi engelleyin.";
    } else if (riskScore > 60) {
        verdict = "YÜKSEK RİSK - GÜÇLÜ OLTALAMA ŞÜPHESİ";
        recommendation = "Bu sitede kişisel bilgilerinizi girmemeniz şiddetle tavsiye edilir. Dikkatli ilerleyin.";
    } else if (riskScore > 30) {
        verdict = "ORTA RİSK - ŞÜPHELİ UNSURLAR TESPİT EDİLDİ";
        recommendation = "Bu siteye karşı dikkatli olun. Girdiğiniz bilgilere ve tıkladığınız linklere özen gösterin.";
    }

    // 4. Build the final JSON output
    const result = {
        risk_score: riskScore,
        confidence: 0.92, // Placeholder confidence score
        verdict: verdict,
        analysis_summary: `URL, içerik ve kullanıcı girdisi analizine dayanarak, bu sayfa ${riskScore} puanla "${verdict}" olarak değerlendirilmiştir.`,
        detailed_breakdown: {
            url_analysis: urlAnalysis,
            content_analysis: contentAnalysis,
            brand_analysis: brandAnalysis,
            input_analysis: inputAnalysis,
            social_engineering_analysis: socialEngineeringAnalysis,
        },
        recommendation: recommendation
    };

    return result;
}

// Sub-analysis functions for each criterion

function analyzeUrl(url) {
    let score = 0;
    let reasons = [];
    if (!url) return { score: 0, reason: "URL sağlanmadı." };

    // Check for IP address usage
    if (/^https?:\/\/\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/.test(url)) {
        score = 100;
        reasons.push("URL, bir alan adı yerine doğrudan bir IP adresi kullanıyor.");
    }

    // Check for suspicious keywords
    const suspiciousKeywords = ['login', 'confirm', 'account', 'secure', 'verify', 'update'];
    if (suspiciousKeywords.some(keyword => url.includes(keyword))) {
        score = Math.min(score + 40, 100);
        reasons.push("URL'de 'login', 'secure' gibi şüpheli anahtar kelimeler bulunuyor.");
    }

    // Check for lack of HTTPS
    if (!url.startsWith('https://')) {
        score = Math.min(score + 50, 100);
        reasons.push("Güvenli HTTPS protokolü kullanılmıyor.");
    } else {
         reasons.push("HTTPS kullanılıyor, ancak bu tek başına güvenli olduğu anlamına gelmez.");
    }

    return { score: score, reason: reasons.join(' ') || "URL'de belirgin bir risk tespit edilmedi." };
}

function analyzeContent(text, title) {
    let score = 0;
    let reasons = [];
    const fullText = (title + ' ' + text).toLowerCase();

    // Check for urgency and fear language
    const urgencyWords = ['urgent', 'important', 'action required', 'hemen', 'acil', 'gerekli'];
    if (urgencyWords.some(word => fullText.includes(word))) {
        score = Math.min(score + 60, 100);
        reasons.push("Aciliyet ve anında eylem gerektiren bir dil kullanılmış.");
    }

    // Check for spelling/grammar mistakes (simple check)
    const commonMistakes = ['hesabiniz', 'şifrenizi', 'onaylayin']; // Simple check for common non-standard turkish chars
    if (commonMistakes.some(word => fullText.includes(word))) {
        score = Math.min(score + 30, 100);
        reasons.push("Metinde potansiyel yazım hataları veya resmi olmayan dil kullanımı tespit edildi.");
    }

    return { score: score, reason: reasons.join(' ') || "İçerikte belirgin bir riskli dil tespit edilmedi." };
}

function analyzeBrand(brand_indicators, url) {
    let score = 0;
    let reasons = [];
    if (!brand_indicators || !url) return { score: 0, reason: "Marka veya URL bilgisi eksik." };

    const brandName = brand_indicators.toLowerCase().replace(' logo', '');
    if (!url.includes(brandName.split(' ')[0])) {
        score = 90;
        reasons.push(`Sayfada '${brand_indicators}' markasından bahsediliyor ancak bu marka URL'de geçmiyor, bu bir taklit olabilir.`);
    }

    return { score: score, reason: reasons.join(' ') || "Marka ve URL arasında bir tutarsızlık bulunmadı." };
}

function analyzeInputs(input_fields) {
    if (!input_fields || input_fields.length === 0) {
        return { score: 0, reason: "Sayfada herhangi bir kullanıcı giriş alanı bulunmuyor." };
    }

    let score = 0;
    let reasons = [];
    const sensitiveInputs = ['password', 'credit-card', 'ssn', 'cvv'];

    if (input_fields.includes('password')) {
        score = Math.min(score + 70, 100);
        reasons.push("Şifre girişi isteniyor.");
    }
    if (input_fields.includes('email') || input_fields.includes('username')) {
        score = Math.min(score + 20, 100);
        reasons.push("Kullanıcı adı veya e-posta isteniyor.");
    }
    if (sensitiveInputs.some(field => input_fields.includes(field))) {
        score = 100; // High score for credit card or SSN
        reasons.push("Kredi kartı veya SSN gibi çok hassas bilgiler isteniyor.");
    }

    return { score: score, reason: reasons.join(' ') || "Hassas bilgi girişi istenmiyor." };
}

function analyzeSocialEngineering(text) {
    let score = 0;
    let reasons = [];
    if (!text) return { score: 0, reason: "Metin içeriği yok." };
    const lowerText = text.toLowerCase();

    // Check for reward or punishment language
    const rewardWords = ['kazandınız', 'ödül', 'tebrikler', 'ödülünüz'];
    const punishmentWords = ['hesabınız askıya alındı', 'askıya alınacak', 'kapatılacak', 'sınırlı'];

    if (rewardWords.some(word => lowerText.includes(word))) {
        score = Math.min(score + 70, 100);
        reasons.push("Kullanıcıyı cezbedecek bir ödül veya hediye vaadi kullanılıyor.");
    }
    if (punishmentWords.some(word => lowerText.includes(word))) {
        score = Math.min(score + 80, 100);
        reasons.push("Hesap kapatma veya askıya alma gibi bir ceza tehdidi ile korku yaratılıyor.");
    }

    return { score: score, reason: reasons.join(' ') || "Belirgin bir sosyal mühendislik taktiği tespit edilmedi." };
}
