# MHRS Randevu Bulucu

Bu program, MHRS (Merkezi Hekim Randevu Sistemi) üzerinden otomatik olarak randevu aramak ve bulunduğunda bildirim almak için geliştirilmiştir.

## Özellikler

- Otomatik MHRS girişi
- Belirtilen tarih aralığında randevu arama
- Hastane ve klinik filtreleme
- Doktor adına göre filtreleme
- Sesli ve görsel bildirimler
- E-posta bildirimleri
- Detaylı loglama

## Kurulum

1. Python 3.8 veya daha yüksek bir sürüm yükleyin
2. Gerekli paketleri yükleyin:
   ```bash
   pip install selenium webdriver-manager
   ```
3. Chrome tarayıcısının yüklü olduğundan emin olun

## E-posta Bildirimi Ayarları

Program, randevu bulunduğunda e-posta bildirimi gönderebilir. Bunun için Gmail hesabınızda bazı ayarlamalar yapmanız gerekiyor:

### 1. Gmail Hesap Ayarları

1. Gmail hesabınıza giriş yapın
2. Sağ üst köşedeki profil resminize tıklayın
3. "Google Hesabını Yönet" seçeneğine tıklayın
4. Sol menüden "Güvenlik" seçeneğine tıklayın
5. "2 Adımlı Doğrulama"yı bulun ve etkinleştirin
6. 2 Adımlı Doğrulama etkinleştirildikten sonra, aynı sayfada "Uygulama Şifreleri" seçeneğini bulun
7. "Uygulama Seç" dropdown menüsünden "Diğer" seçeneğini seçin
8. İsim olarak "MHRS Randevu Bulucu" yazın
9. "Oluştur" butonuna tıklayın
10. Size 16 haneli bir şifre verilecek. Bu şifreyi kopyalayın

### 2. Config Dosyası Ayarları

`config.json` dosyasında e-posta ayarlarınızı yapılandırın:

```json
{
    "IdentificationNum": "TC_KIMLIK_NO",
    "Password": "MHRS_SIFRE",
    "City": "SEHIR_ADI",
    "District": "ILCE_ADI",
    "Clinic": "KLINIK_ADI",
    "Hospital": "HASTANE_ADI",
    "DoctorName": "DOKTOR_ADI",
    "StartDate": "BASLANGIC_TARIHI",
    "EndDate": "BITIS_TARIHI",
    "Email": "GMAIL_ADRESINIZ",
    "EmailPassword": "UYGULAMA_SIFRESI"
}
```

Örnek:
```json
{
    "IdentificationNum": "12345678901",
    "Password": "sifrem123",
    "City": "Ankara",
    "District": "YENİMAHALLE",
    "Clinic": "İç Hastalıkları (Dahiliye)",
    "Hospital": "ANKARA ETLİK ŞEHİR HASTANESİ",
    "DoctorName": "ALPER ŞENKALFA",
    "StartDate": "13.05.2025",
    "EndDate": "14.05.2025",
    "Email": "ornek@gmail.com",
    "EmailPassword": "abcd efgh ijkl mnop"
}
```

## Kullanım

1. `config.json` dosyasını kendi bilgilerinizle düzenleyin
2. Programı çalıştırın:
   ```bash
   python main.py
   ```

## Önemli Notlar

- Program her 10 dakikada bir randevu kontrolü yapar
- Randevu bulunduğunda sesli bildirim verir ve e-posta gönderir
- Hata durumunda 5 dakika bekleyip tekrar dener
- Tüm işlemler `mhrs_randevu.log` dosyasına kaydedilir
- Doktor adı filtresi opsiyoneldir, boş bırakılabilir veya config dosyasından kaldırılabilir

## Sorun Giderme

### E-posta Bildirimi Sorunları

1. **SMTP Hatası**: Gmail hesabınızda 2 Adımlı Doğrulama'nın etkin olduğundan ve doğru uygulama şifresini kullandığınızdan emin olun
2. **Bağlantı Hatası**: İnternet bağlantınızı kontrol edin
3. **Kimlik Doğrulama Hatası**: E-posta adresi ve uygulama şifresinin doğru olduğundan emin olun

### Diğer Sorunlar

1. **Giriş Hatası**: TC Kimlik No ve şifrenin doğru olduğundan emin olun
2. **Element Bulunamadı Hatası**: MHRS sitesinin yapısı değişmiş olabilir, lütfen bildirin
3. **Tarayıcı Hatası**: Chrome'un güncel sürümünü kullandığınızdan emin olun
4. **Doktor Seçim Hatası**: Doktor adının tam olarak MHRS sistemindeki gibi yazıldığından emin olun

## Güvenlik

- `config.json` dosyasında hassas bilgileriniz (TC Kimlik No, şifre, e-posta şifresi) bulunmaktadır
- Bu dosyayı güvenli bir şekilde saklayın ve başkalarıyla paylaşmayın
- E-posta şifrenizi düzenli olarak değiştirmeniz önerilir

## Katkıda Bulunma

1. Bu depoyu fork edin
2. Yeni bir branch oluşturun (`git checkout -b feature/yeniOzellik`)
3. Değişikliklerinizi commit edin (`git commit -am 'Yeni özellik: Açıklama'`)
4. Branch'inizi push edin (`git push origin feature/yeniOzellik`)
5. Pull Request oluşturun
