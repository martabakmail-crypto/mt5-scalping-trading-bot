# 🤖 Python MetaTrader 5 (MT5) Cent Scalping Trading Bot

Bot trading scalping otomatis berbasis Python yang terhubung langsung ke terminal MetaTrader 5 (MT5) untuk Akun Cent (Exness, FBS, XM, dll).

---

## 🌟 Fitur Utama

- **Multi-Indicator Weighted Scoring (≥ 70% Confidence Threshold):**
  - **Trend (30%):** EMA 50 & EMA 200 direction.
  - **Momentum (25%):** RSI 14 (Oversold/Overbought & Pullbacks).
  - **Price Action (25%):** Candlestick Wick Rejection & Engulfing pattern.
  - **Volatility (20%):** Average True Range (ATR) expansion.
- **Akun Cent Suffix Compatibility:** Mendukung simbol khusus cent seperti `XAUUSDc`, `EURUSDc`, `XAUUSDm`.
- **Auto ATR TP/SL & Dynamic Trailing Stop:** Memasang SL dan TP otomatis berbasis ATR pada setiap transaksi, serta mengunci profit dengan *Breakeven / Trailing Stop*.
- **Max Spread Protection:** Mencegah entry saat spread broker melebar tajam.
- **Telegram Push Alerts:** Notifikasi realtime ke HP setiap kali transaksi dibuka, ditutup, atau rangkuman status saldo.

---

## 📁 Struktur File

```
scalping_bot/
├── config.py           # Konfigurasi bot (Lot, ATR, Symbol, Telegram)
├── signal_engine.py    # Mesin analisis teknikal & kalkulasi skor sinyal (0-100%)
├── risk_manager.py     # Pengelola risiko (Lot size, Auto TP/SL ATR, Trailing Stop)
├── telegram_notify.py  # Modul notifikasi ke Telegram HP
├── main.py             # Main loop & koneksi MT5 Terminal
├── requirements.txt    # Daftar dependensi Python
└── .env.example        # Template konfigurasi environment
```

---

## 🚀 Cara Menjalankan Bot

### 1. Install Dependensi Python
```bash
pip install -r requirements.txt
```

### 2. Konfigurasi File `.env`
Salin file `.env.example` menjadi `.env` dan sesuaikan nilainya:
```bash
cp .env.example .env
```
Isi variabel:
- `SYMBOL=XAUUSDc` (atau `EURUSDc` sesuai broker cent Anda)
- `TELEGRAM_BOT_TOKEN` & `TELEGRAM_CHAT_ID` (dari `@BotFather`)

### 3. Pastikan Terminal MT5 Aktif
- Unduh & Install **MetaTrader 5 Desktop Client** dari halaman resmi atau mirror broker:
  - **Halaman Resmi MetaTrader 5:** [https://www.metatrader5.com/en/download](https://www.metatrader5.com/en/download)
  - **Halaman Download Exness:** [https://www.exness.com/metatrader-5/](https://www.exness.com/metatrader-5/)
- Buka aplikasi **MetaTrader 5** dan Login ke akun Exness Anda:
  - **Server:** `Exness-MT5Trial` (atau server akun Exness Anda)
  - **Login:** ID Akun Anda (misal `416378891`)
  - **Password:** Password akun trading Anda
- Pastikan opsi **"Allow Algo Trading"** sudah dicentang di MT5 (Tools -> Options -> Expert Advisors).
- Pastikan simbol `XAUUSD` / `XAUUSDc` sudah ditambahkan ke daftar **Market Watch** MT5.



### 4. Jalankan Bot
```bash
python main.py
```

---

## 🛡️ Catatan Penting Penggunaan
- Selalu uji bot terlebih dahulu di **Akun Demo / Akun Cent dengan lot minimum (0.01 cent lot)**.
- Gunakan VPS Windows dengan latensi rendah (< 10ms) ke server broker untuk eksekusi scalping optimal 24/7.
