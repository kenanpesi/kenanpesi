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
```

## Kullanım

- `/register` - Yeni kullanıcı kaydı
- `/login` - Kullanıcı girişi
- `/dashboard` - Kullanıcı paneli ve erişim logları

## Güvenlik

- Şifreler hash'lenerek saklanır
- Flask-Login ile oturum yönetimi
- SQL injection koruması
