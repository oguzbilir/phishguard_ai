import tweepy
import pandas as pd
import os

# Twitter API v2 için Bearer Token'ınızı buraya girin.
# Güvenlik için bu anahtarı doğrudan kod içerisine yazmak yerine,
# ortam değişkeni olarak ayarlamanız önerilir.
BEARER_TOKEN = "YOUR_BEARER_TOKEN_HERE"

def search_tweets(client, query, max_results=10):
    """
    Belirtilen sorgu ile tweetleri arar ve ilgili metrikleri toplar.
    """
    try:
        # Twitter API v2'nin search_recent_tweets metodunu kullanarak arama yapma
        # public_metrics ile beğeni, retweet, yorum ve alıntı sayılarını alıyoruz.
        response = client.search_recent_tweets(
            query=query,
            max_results=max_results,
            tweet_fields=["public_metrics", "created_at"]
        )

        # Eğer arama sonucu boş ise
        if not response.data:
            print("Belirtilen kriterlere uygun tweet bulunamadı.")
            return []

        tweets = []
        for tweet in response.data:
            metrics = tweet.public_metrics
            tweets.append({
                "id": tweet.id,
                "text": tweet.text,
                "created_at": tweet.created_at,
                "like_count": metrics['like_count'],
                "retweet_count": metrics['retweet_count'],
                "reply_count": metrics['reply_count'],
                "quote_count": metrics['quote_count']
            })

        print(f"Toplam {len(tweets)} adet tweet bulundu.")
        return tweets

    except Exception as e:
        print(f"Tweet arama sırasında bir hata oluştu: {e}")
        return []

def main():
    """
    Ana fonksiyon, betiğin başlangıç noktası.
    """
    print("Twitter veri çekme betiği başlatılıyor...")

    # Tweepy istemcisini Bearer Token ile başlatma
    try:
        # Bearer token'ın yer tutucu olup olmadığını kontrol et
        if BEARER_TOKEN == "YOUR_BEARER_TOKEN_HERE" or not BEARER_TOKEN:
            print("Hata: Lütfen geçerli bir Bearer Token girin.")
            return

        client = tweepy.Client(BEARER_TOKEN)
        print("Twitter API'sine başarıyla bağlandı.")
    except Exception as e:
        print(f"Hata: Twitter API'sine bağlanılamadı. Lütfen Bearer Token'ınızı kontrol edin.")
        print(f"Detaylar: {e}")
        return

    # Örnek arama sorgusu ve maksimum sonuç sayısı
    search_query = "yapay zeka -is:retweet"  # "yapay zeka" içeren ve retweet olmayan tweetler
    max_tweet_count = 20

    # Tweetleri ara
    found_tweets = search_tweets(client, search_query, max_tweet_count)

    # Bulunan tweetleri ekrana yazdır (test amaçlı)
    if found_tweets:
        print("\nBulunan ilk 5 tweet:")
        for tweet in found_tweets[:5]:
            print(f"- {tweet['text'][:80]}...")

        # Verileri CSV dosyasına kaydet
        save_tweets_to_csv(found_tweets, "tweets.csv")

def save_tweets_to_csv(tweets, filename):
    """
    Tweet listesini bir CSV dosyasına kaydeder.
    """
    if not tweets:
        print("Kaydedilecek tweet bulunamadı.")
        return

    try:
        df = pd.DataFrame(tweets)
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"Veriler başarıyla '{filename}' dosyasına kaydedildi.")
    except Exception as e:
        print(f"CSV dosyasına kaydetme sırasında bir hata oluştu: {e}")

if __name__ == "__main__":
    main()
