# 🎯 Akıllı Log Analizi ve Anomali Tespit Asistanı - Task Listesi

## 1. Proje Altyapısı ve Kurulum

- [x] Proje klasör yapısını oluştur
- [x] Docker Compose dosyasını oluştur
- [x] FastAPI backend projesini başlat
- [x] React frontend projesini başlat
- [x] Shadcn/ui ve Tailwind'i frontend'e entegre et
- [x] SQLite veritabanını kur ve bağlantıyı test et

## 2. Kimlik Doğrulama (Opsiyonel, MVP'de girişsiz olabilir)

- [ ] Giriş/Kayıt ol ekranı tasarla
- [ ] E-posta & şifre ile giriş/kayıt olma fonksiyonunu ekle
- [ ] Google OAuth ile giriş desteği ekle
- [ ] Şifremi unuttum akışını ekle

## 3. Dashboard

- [ ] Navbar bileşenini oluştur ("Loglarım", "Yeni Yükle", "Bildirimler", "Ayarlar" sekmeleri)
- [ ] Aktif log sayısı kartını ekle
- [ ] Son 7 günlük anomali grafiğini ekle
- [ ] En çok hata üreten sistem kartını ekle
- [ ] "Yeni Analiz Başlat" butonunu ekle

## 4. Log Yükleme

- [ ] Log yükleme ekranı tasarla (drag & drop alanı)
- [ ] Desteklenen formatları göster (.csv, .log, .json)
- [ ] "Log Formatı Seç" dropdown'ı ekle
- [ ] "Yükle ve Önizle" butonunu ekle
- [ ] Örnek log dosyası indirme linki ekle
- [ ] Backend'de dosya yükleme endpoint'i oluştur
- [ ] Yüklenen dosyanın boyutunu kontrol et (max 50MB)
- [ ] Hatalı formatlarda kullanıcıya uyarı göster

## 5. Log Önizleme ve Onay

- [ ] İlk 10 satırı tablo olarak göster
- [ ] Kolonları ayarla ("Zaman damgası", "Hata tipi", "Açıklama")
- [ ] "Analize Başla" butonunu ekle
- [ ] "Geri dön" linkini ekle
- [ ] Satır renklendirme fonksiyonunu ekle

## 6. Analiz İşleniyor Ekranı

- [ ] İlerleme çubuğu ekle (% olarak)
- [ ] "Bu sırada ne yapıyoruz?" açıklama metni ekle
- [ ] Loading animasyonu ekle

## 7. AI Modeli ve Anomali Tespiti

- [ ] RandomForestClassifier + TF-IDF pipeline'ını hazırla
- [ ] Satır uzunluğu, büyük harf, özel karakter, tarih/IP/port, TF-IDF öznitelik çıkarım fonksiyonlarını yaz
- [ ] Modeli örnek veriyle eğit
- [ ] Modeli kaydet ve yükle
- [ ] Yüklenen log dosyasını modele gönder
- [ ] Anomali tespit edilen satırları işaretle
- [ ] Kritik seviyeli satırları belirle
- [ ] Model cevap süresini test et (≤ 1 sn)

## 8. Analiz Sonucu – Özet

- [ ] Toplam log sayısını göster
- [ ] Toplam anomali sayısını göster
- [ ] En çok görülen 3 hata tipini listele
- [ ] Zaman serisinde hata sıklığı grafiğini ekle
- [ ] "Detayları Gör" butonunu ekle

## 9. Detaylı Anomali Görüntüleme

- [ ] Log ID, zaman damgası, ciddiyet seviyesi, açıklama ve hata türünü göster
- [ ] Satırları card veya accordion olarak göster
- [ ] "Log'a Git" ve "Raporla" butonlarını ekle

## 10. Bildirim Sistemi

- [ ] Toast/modal bildirim sistemi kur
- [ ] Kritik anomali tespitinde bildirim göster
- [ ] Bildirimde anomali detayını sun
- [ ] E-posta bildirimleri toggle'ı ekle
- [ ] Slack entegrasyonu (Webhook URL alanı) ekle
- [ ] Ciddiyet seviyesine göre bildirim ayarları ekle
- [ ] Test bildirimi gönderme butonu ekle

## 11. Log Arama ve Filtreleme

- [ ] Arama kutusu ekle (full-text)
- [ ] Tarih aralığı seçici ekle
- [ ] Hata tipi dropdown'ı ekle
- [ ] "Sadece anomalileri göster" checkbox'ı ekle
- [ ] Sonuçlarda keyword highlight özelliği ekle
- [ ] Liste/Tablo görünümünü uygula

## 12. Ayarlar / Kullanıcı Yönetimi

- [ ] API anahtarı oluşturma ve yenileme fonksiyonu ekle
- [ ] Kullanıcı ekle/sil (rol belirleme: admin, viewer)
- [ ] Veri saklama süresi seçimi ekle (örn. 30 gün, 90 gün)
- [ ] Abonelik planı bilgisini göster
- [ ] Ayar sekmelerini kartlar halinde böl

## 13. Güvenlik ve Gizlilik

- [ ] IP adresi, kullanıcı adı gibi PII verileri maskele
- [ ] Log ID üzerinden anonimleştirme uygula
- [ ] Verileri 30 gün sakla, sonra sil

## 14. Test ve Kabul

- [ ] Her özelliğin kabul kriterlerine göre testini yap
- [ ] Performans testleri uygula (analiz süresi < 2 sn, yükleme < 5 sn)
- [ ] Yanlış pozitif oranını ölç (%5'ten az olmalı)
- [ ] Model doğruluğunu ölç (%95'ten fazla olmalı)

---

**Toplam Task Sayısı:** 67
**Tamamlanan:** 6
**Kalan:** 61

---

*Bu dosya, proje ilerledikçe güncellenecektir. Her tamamlanan task için checkbox işaretlenecektir.* 