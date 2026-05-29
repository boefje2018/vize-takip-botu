import asyncio
from utils.helpers import load_config, load_env, timestamp, format_alert
from notifiers.telegram import TelegramNotifier
from notifiers.email_notifier import EmailNotifier


SCRAPERS = {}


def register_scrapers(config: dict):
    global SCRAPERS
    SCRAPERS.clear()

    svc = config["services"]

    if svc["tlscontact"]["enabled"]:
        from scrapers.tlscontact import TLScontactScraper
        SCRAPERS["TLScontact"] = TLScontactScraper(svc["tlscontact"])

    if svc["vfsglobal"]["enabled"]:
        from scrapers.vfsglobal import VFSGlobalScraper
        SCRAPERS["VFS Global"] = VFSGlobalScraper(svc["vfsglobal"])

    if svc["ustraveldocs"]["enabled"]:
        us_config = {
            "centers": svc["ustraveldocs"]["centers"],
            "username": svc["ustraveldocs"].get("username", ""),
            "password": svc["ustraveldocs"].get("password", ""),
        }
        if not us_config["username"] or not us_config["password"]:
            print("⚠ ABD vizesi için kullanıcı adı/şifre config.json'a eklenmedi, pasif.")
        else:
            from scrapers.ustraveldocs import USTravelDocsScraper
            SCRAPERS["US Travel Docs"] = USTravelDocsScraper(us_config)


async def check_all(telegram: TelegramNotifier, email: EmailNotifier):
    tasks = []
    centers_info = []

    for name, scraper in SCRAPERS.items():
        for center in scraper.centers:
            if center.get("skip"):
                continue
            tasks.append(scraper.check(center))
            centers_info.append((name, center["name"]))

    if not tasks:
        return []

    results = await asyncio.gather(*tasks)

    new_slots = [r for r in results if r.has_slot]
    errors = [r for r in results if r.error and not r.has_slot]

    status = f"[{timestamp()}] {len(results)} merkez tarandı | "
    status += f"✅ {len(new_slots)} boş slot | "
    status += f"⚠ {len(errors)} hata"

    if new_slots:
        for result in new_slots:
            alert = format_alert(result)
            print("\n" + alert + "\n")
            telegram.send(alert)
            email.send(f"Vize Randevusu {result.service} - {result.center}", alert)

    print(status)

    if errors:
        for r in errors:
            print(f"  ⚠ {r.service} - {r.center}: {r.error}")

    return new_slots


def main():
    load_env()
    config = load_config()
    register_scrapers(config)

    telegram = TelegramNotifier()
    email = EmailNotifier()

    interval = config.get("check_interval_minutes", 5)

    print("╔══════════════════════════════════════════╗")
    print("║     VİZE RANDEVU TAKİP SİSTEMİ          ║")
    print("╚══════════════════════════════════════════╝")
    print(f" Kontrol aralığı: {interval} dakika")
    print(f" Takip edilen: {', '.join(SCRAPERS.keys())}")
    print(f" Telegram: {'✅ Aktif' if telegram.enabled else '❌ Devre Dışı'}")
    print(f" E-posta : {'✅ Aktif' if email.enabled else '❌ Devre Dışı'}")
    print(f" Toplam merkez: {sum(len(s.centers) for s in SCRAPERS.values())}")
    print("─" * 46)

    is_ci = "CI" in __import__("os").environ

    async def run():
        while True:
            try:
                await check_all(telegram, email)
            except Exception as e:
                print(f"❌ Kritik hata: {e}")
            if is_ci:
                break
            await asyncio.sleep(interval * 60)

    asyncio.run(run())


if __name__ == "__main__":
    main()
