<<<<<<< HEAD
# Remote PC Access

Bu uygulama, web tarayıcısı üzerinden uzaktan bilgisayar erişimi sağlar.

## Özellikler

- Web tabanlı arayüz
- Gerçek zamanlı komut çalıştırma
- Birden fazla bilgisayar desteği
- Kolay kurulum

## Kurulum

### Web Sunucusu

```bash
cd web-server
npm install
npm start
```

### Electron Uygulaması

```bash
cd hack-terminal
npm install
npm start
=======
# Login Sistemi

Bu proje, Flask kullanılarak oluşturulmuş basit bir login ve kayıt sistemi içerir. Sistem aynı zamanda uzaktan erişen kullanıcıların IP adreslerini ve erişim zamanlarını kaydeder.

## Özellikler

- Kullanıcı kaydı
- Kullanıcı girişi
- Erişim logları (IP adresi ve zaman)
- Güvenli şifre saklama
- Responsive tasarım

## Kurulum

1. Repoyu klonlayın:
```bash
git clone [REPO_URL]
```

2. Gerekli paketleri yükleyin:
```bash
pip install -r requirements.txt
```

3. Uygulamayı çalıştırın:
```bash
python app.py
>>>>>>> 0a39acc8ee25066047bf5606fb695e6f99d15663
```

## Kullanım

<<<<<<< HEAD
1. Web sunucusunu başlatın
2. Electron uygulamasını bilgisayarınızda çalıştırın
3. Web tarayıcınızdan `http://localhost:3000` adresine gidin
4. Bağlı bilgisayarı seçin ve komutları çalıştırın

## Güvenlik

Bu uygulama sadece güvenilir ağlarda kullanılmalıdır. Güvenlik önlemleri almadan internete açık şekilde kullanmayın.
=======
- `/register` - Yeni kullanıcı kaydı
- `/login` - Kullanıcı girişi
- `/dashboard` - Kullanıcı paneli ve erişim logları

## Güvenlik

- Şifreler hash'lenerek saklanır
- Flask-Login ile oturum yönetimi
- SQL injection koruması
>>>>>>> 0a39acc8ee25066047bf5606fb695e6f99d15663
