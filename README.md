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
```

## Kullanım

1. Web sunucusunu başlatın
2. Electron uygulamasını bilgisayarınızda çalıştırın
3. Web tarayıcınızdan `http://localhost:3000` adresine gidin
4. Bağlı bilgisayarı seçin ve komutları çalıştırın

## Güvenlik

Bu uygulama sadece güvenilir ağlarda kullanılmalıdır. Güvenlik önlemleri almadan internete açık şekilde kullanmayın.
