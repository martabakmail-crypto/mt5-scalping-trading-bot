# 🤖 MIFX (Monex Investindo Futures) Auto SL/TP Scalping Trading Bot

Bot trading otomatis berbasis Python yang dirancang khusus untuk akun **MIFX (Monex)** dengan fitur **Auto SL, Auto TP, dan Trailing Stop Otomatis**.

---

## 🌟 Fitur Utama MIFX Bot

1. **Auto Stop Loss (SL) & Take Profit (TP) Berbasis ATR:**
   - **Stop Loss (SL):** Terhitung & terpasang otomatis di jarak `1.5 * ATR` dari titik entry.
   - **Take Profit (TP):** Terhitung & terpasang otomatis di jarak `2.25 * ATR` (Rasio Risk:Reward ~ 1:1.5).
2. **Auto Breakeven & Dynamic Trailing Stop:**
   - Ketika transaksi profit mencapai `1.0 * ATR`, bot otomatis menggeser SL ke titik Entry (*Risk-Free Trade*).
   - Trailing SL bergeser mengunci profit setiap pergerakan `0.5 * ATR`.
3. **Multi-Indicator Weighted Scoring (≥ 70% Confidence Threshold):**
   - EMA 50 & 200 Trend Filter.
   - RSI 14 Oversold / Overbought.
   - ATR Volatility Expansion.
4. **Notifikasi Telegram Realtime:**
   - Laporan transaksi langsung dikirim ke Telegram HP Anda (`@antdeb13_bot`) saat order dibuka, SL bergeser, atau transaksi ditutup.

---

## 📁 Struktur File

```
mifx_bot/
├── config.py           # Konfigurasi akun MIFX, Simbol, Lot, SL/TP ATR
├── risk_manager.py     # Modul Auto SL/TP & Trailing Stop
├── telegram_notify.py  # Modul notifikasi Telegram HP
├── main.py             # Engine utama & scanning chart
├── requirements.txt    # Dependensi Python
└── README.md           # Panduan penggunaan
```
