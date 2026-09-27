import os
import time
import requests

# --- AYARLAR (GitHub Secrets'tan otomatik çeker) ---
WEATHER_API_KEY = os.environ.get("WEATHER_API_KEY")
SEHIR = "Konya"

PUSHOVER_TOKEN = os.environ.get("PUSHOVER_TOKEN")
PUSHOVER_USER_KEY = os.environ.get("PUSHOVER_USER_KEY")


def hava_durumunu_kontrol_et():
  url = f"http://api.openweathermap.org/data/2.5/weather?q={SEHIR}&appid={WEATHER_API_KEY}&units=metric&lang=tr"
  try:
    response = requests.get(url)
    veri = response.json()

    if response.status_code == 200:
      sicaklik = veri["main"]["temp"]
      nem = veri["main"]["humidity"]
      durum = veri["weather"][0]["description"]

      yagis_var_mi = any(
          "yağmur" in w["description"].lower() for w in veri["weather"]
      )

      return {
          "sicaklik": sicaklik,
          "nem": nem,
          "durum": durum,
          "yagis": yagis_var_mi,
      }
    else:
      print("Hava durumu verisi alınamadı:", veri.get("message"))
      return None
  except Exception as e:
    print("Bağlantı hatası:", e)
    return None


def pushover_bildirim_gonder(baslik, mesaj):
  url = "https://api.pushover.net/1/messages.json"
  payload = {
      "token": PUSHOVER_TOKEN,
      "user": PUSHOVER_USER_KEY,
      "title": baslik,
      "message": mesaj,
      "sound": "magic",
  }
  try:
    requests.post(url, data=payload)
    print("Pushover bildirimi telefona gönderildi!")
  except Exception as e:
    print("Bildirim gönderilemedi:", e)


def ucus_kosullarini_degerlendir(hava):
  sicaklik = hava["sicaklik"]
  nem = hava["nem"]
  durum = hava["durum"]

  print(
      f"Güncel Konya Durumu -> Sıcaklık: {sicaklik}°C | Nem: %{nem} | Hava:"
      f" {durum}"
  )

  if 20 <= sicaklik <= 30 and nem >= 45:
    mesaj = (
        f"Kritik Şartlar Sağlandı!\nSıcaklık: {sicaklik}°C\nNem: %{nem}\nHava:"
        f" {durum}\n\nHemen dışarı çıkıp parkları ve sokak lambalarını kontrol"
        " et!"
    )
    pushover_bildirim_gonder("🐜 Konya Karınca Uçuş Alarmı!", mesaj)
  else:
    print("Şartlar henüz uçuş için uygun değil, sonraki kontrole geçiliyor...\n")


if __name__ == "__main__":
  print("Karınca Uçuş Takip Botu Başlatıldı...")
  hava_verisi = hava_durumunu_kontrol_et()
  if hava_verisi:
    ucus_kosullarini_degerlendir(hava_verisi)
