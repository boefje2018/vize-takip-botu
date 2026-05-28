import json
from datetime import datetime
from pathlib import Path


def load_config(path: str = "config.json") -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_env(path: str = ".env"):
    env_file = Path(path)
    if not env_file.exists():
        return
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        import os
        os.environ.setdefault(key.strip(), value.strip())


def timestamp() -> str:
    return datetime.now().strftime("%d.%m.%Y %H:%M:%S")


TLSCONTACT_URLS = {
    "Almanya": "https://de.tlscontact.com/tr/IST/page.php?p=appointment",
    "Fransa": "https://fr.tlscontact.com/tr/IST/page.php?p=appointment",
    "Hollanda": "https://nl.tlscontact.com/tr/IST/page.php?p=appointment",
    "Belçika": "https://be.tlscontact.com/tr/IST/page.php?p=appointment",
    "UK (TLS)": "https://www.tlscontact.com/uk/tr/page.php?p=appointment",
}

VFSCLOBAL_URLS = {
    "İtalya": "https://www.vfsglobal.com/italy/turkey/schedule-an-appointment.html",
    "İspanya": "https://visa.vfsglobal.com/tur/en/esp/book-an-appointment",
    "Yunanistan": "https://visa.vfsglobal.com/tur/en/grc/book-an-appointment",
    "Kanada": "https://visa.vfsglobal.com/tur/en/can/book-an-appointment",
    "Polonya": "https://visa.vfsglobal.com/tur/en/pol/book-your-appointment",
    "İsviçre": "https://visa.vfsglobal.com/tur/en/che/book-an-appointment",
    "Avusturya": "https://visa.vfsglobal.com/tur/en/aut/book-an-appointment",
    "Portekiz": "https://visa.vfsglobal.com/tur/en/prt/book-an-appointment",
    "Macaristan": "https://visa.vfsglobal.com/tur/en/hun/book-an-appointment",
    "Çekya": "https://visa.vfsglobal.com/tur/en/cze/book-an-appointment",
    "Danimarka": "https://visa.vfsglobal.com/tur/en/dnk/book-an-appointment",
    "İsveç": "https://visa.vfsglobal.com/tur/en/swe/book-an-appointment",
    "Norveç": "https://visa.vfsglobal.com/tur/en/nor/book-an-appointment",
    "Finlandiya": "https://visa.vfsglobal.com/tur/en/fin/book-an-appointment",
    "Avustralya": "https://visa.vfsglobal.com/tur/en/aus/book-an-appointment",
    "Hırvatistan": "https://visa.vfsglobal.com/tur/en/hrv/book-an-appointment",
    "Bulgaristan": "https://visa.vfsglobal.com/tur/en/bgr/book-an-appointment",
    "Romanya": "https://visa.vfsglobal.com/tur/en/rou/book-an-appointment",
    "Malta": "https://visa.vfsglobal.com/tur/en/mlt/book-an-appointment",
    "Slovakya": "https://visa.vfsglobal.com/tur/en/svk/book-an-appointment",
    "Slovenya": "https://visa.vfsglobal.com/tur/en/svn/book-an-appointment",
    "Estonya": "https://visa.vfsglobal.com/tur/en/est/book-an-appointment",
    "Letonya": "https://visa.vfsglobal.com/tur/en/lva/book-an-appointment",
    "Litvanya": "https://visa.vfsglobal.com/tur/en/ltu/book-an-appointment",
}

USDOCS_URLS = {
    "ABD": "https://ais.usvisa-info.com/en-tr/niv",
}


def get_center_url(result) -> str:
    if result.service == "TLScontact":
        return TLSCONTACT_URLS.get(result.center, "")
    elif result.service == "VFS Global":
        return VFSCLOBAL_URLS.get(result.center, "")
    elif result.service == "US Travel Docs":
        return USDOCS_URLS.get(result.center, "")
    return ""


def format_alert(result) -> str:
    url = get_center_url(result)
    lines = [
        "🚨 VİZE RANDEVUSU BULUNDU! 🚨",
        "",
        f"Servis  : {result.service}",
        f"Ülke    : {result.center}",
        f"Tarih   : {timestamp()}",
    ]
    if result.details:
        date_str = extract_dates(result.details)
        if date_str:
            lines.append(f"Müsait  : {date_str}")
        lines.append(f"Detay   : {result.details[:120]}")
    if url:
        lines.append(f"Link    : {url}")
    if result.error:
        lines.append(f"Hata    : {result.error}")
    lines.append("")
    lines.append("Hemen randevu sayfasına gidip işlem yap!")
    return "\n".join(lines)


def extract_dates(text: str) -> str:
    import re
    patterns = [
        r"\b\d{1,2}\s+(Ocak|Şubat|Mart|Nisan|Mayıs|Haziran|Temmuz|Ağustos|Eylül|Ekim|Kasım|Aralık)\s+\d{4}",
        r"\b\d{1,2}\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}",
        r"\b\d{2}\.\d{2}\.\d{4}\b",
        r"\b\d{2}/\d{2}/\d{4}\b",
    ]
    found = []
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        found.extend(matches[:3])
    return ", ".join(found[:3]) if found else ""
