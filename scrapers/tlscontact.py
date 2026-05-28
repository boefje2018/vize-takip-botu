import re
from playwright.async_api import async_playwright
from .base import BaseScraper, CheckResult


class TLScontactScraper(BaseScraper):
    async def check(self, center: dict) -> CheckResult:
        name = center["name"]
        base_url = center["url"]

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                )
                page = await context.new_page()

                appointment_url = base_url.rstrip("/") + "/page.php?p=appointment"
                await page.goto(appointment_url, wait_until="domcontentloaded", timeout=30000)
                await page.wait_for_timeout(3000)

                text = await page.inner_text("body")
                html = await page.inner_html("body")
                await browser.close()

            text = text.lower() if text else ""
            html = html.lower() if html else ""

            # Negative signals
            negative = [
                "no appointment", "no appointments", "currently no",
                "tüm randevular doludur", "randevu bulunmamaktadır",
                "no slot", "no available", "müsait randevu bulunmamaktadır",
                "no dates available",
            ]

            # Strong positive signals
            strong_positive = [
                "choose an appointment", "select a date",
                "available appointment", "appointment available",
                "select appointment",
            ]

            has_negative = any(p in text for p in negative)
            has_strong = any(p in text for p in strong_positive)

            dates = self._extract_dates(text)
            has_time_slot = bool(re.search(r"\b\d{1,2}:\d{2}\b", text))
            has_calendar_widget = bool(re.search(
                r'class="[^"]*calendar[^"]*"|id="[^"]*calendar[^"]*"',
                html
            ))

            if has_negative:
                return CheckResult("TLScontact", name, False, details="Randevu bulunamadı")

            if has_strong and (dates or has_time_slot):
                detail = self._build_detail(dates, text)
                return CheckResult("TLScontact", name, True, details=detail)

            if has_calendar_widget and dates:
                detail = self._build_detail(dates, text)
                return CheckResult("TLScontact", name, True, details=detail)

            return CheckResult("TLScontact", name, False, details="Randevu bulunamadı")

        except Exception as e:
            return CheckResult("TLScontact", name, False, error=str(e))

    def _extract_dates(self, text: str) -> list:
        dates = []
        patterns = [
            r"\b\d{1,2}\s+(Ocak|Şubat|Mart|Nisan|Mayıs|Haziran|Temmuz|Ağustos|Eylül|Ekim|Kasım|Aralık)\s+\d{4}",
            r"\b\d{1,2}\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}",
            r"\b\d{2}\.\d{2}\.\d{4}\b",
        ]
        for pat in patterns:
            matches = re.findall(pat, text, re.IGNORECASE)
            for m in matches:
                full = m[0] if isinstance(m, tuple) else m
                if full not in dates:
                    dates.append(full)
        return dates[:5]

    def _extract_times(self, text: str) -> list:
        times = re.findall(r"\b\d{1,2}:\d{2}\b", text)
        return times[:5]

    def _build_detail(self, dates: list, text: str) -> str:
        parts = []
        if dates:
            parts.append(f"Uygun tarihler: {', '.join(dates)}")
        times = self._extract_times(text)
        if times:
            parts.append(f"Saatler: {', '.join(times)}")
        if not parts:
            parts.append("Randevu bulundu, sayfayı kontrol edin")
        return " | ".join(parts)
