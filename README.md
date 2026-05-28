# Vize Randevu Takip Botu

29 ülke için vize randevu boşluğunu otomatik kontrol eder, Telegram ve e-posta ile bildirim gönderir.

## Nasıl Kullanılır

### 1. Bu repoyu fork'la (kendi hesabına kopyala)

### 2. GitHub Secrets'a bilgilerini ekle

Repo ayarlarından `Settings → Secrets and variables → Actions`:

| Secret | Açıklama |
|---|---|
| `TELEGRAM_BOT_TOKEN` | @BotFather'dan aldığın token |
| `TELEGRAM_CHAT_ID` | @userinfobot'tan aldığın ID |
| `CONFIG_JSON` | `config.json` dosyasının tüm içeriği (JSON) |

### 3. Çalıştır

Her 10 dakikada bir otomatik kontrol eder. Manuel de çalıştırabilirsin: `Actions → Vize Takip → Run workflow`

## Desteklenen Ülkeler

**TLScontact:** Almanya, Fransa, Hollanda, Belçika, UK  
**VFS Global:** İtalya, İspanya, Yunanistan, Kanada, Polonya, İsviçre, Avusturya, Portekiz, Macaristan, Çekya, Danimarka, İsveç, Norveç, Finlandiya, Avustralya, Hırvatistan, Bulgaristan, Romanya, Malta, Slovakya, Slovenya, Estonya, Letonya, Litvanya
