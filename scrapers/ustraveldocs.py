import re
from playwright.async_api import async_playwright
from .base import BaseScraper, CheckResult


class USTravelDocsScraper(BaseScraper):
    LOGIN_URL = "https://ais.usvisa-info.com/en-tr/niv/users/sign_in"
    APPOINTMENT_URL = "https://ais.usvisa-info.com/en-tr/niv/groups/25780260"

    def __init__(self, config: dict):
        super().__init__(config)
        self.username = config.get("username", "")
        self.password = config.get("password", "")

    async def check(self, center: dict) -> CheckResult:
        name = center["name"]

        if not self.username or not self.password:
            return CheckResult("US Travel Docs", name, False,
                               error="ABD vizesi için kullanıcı adı/şifre config.json'a eklenmemiş")

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                )
                page = await context.new_page()

                await page.goto(self.LOGIN_URL, wait_until="domcontentloaded", timeout=30000)
                await page.wait_for_timeout(2000)

                await page.fill('input[name="user[email]"]', self.username)
                await page.fill('input[name="user[password]"]', self.password)
                await page.click('input[name="policy_confirmed"]')
                await page.click('input[type="submit"]')
                await page.wait_for_timeout(5000)

                await page.goto(self.APPOINTMENT_URL, wait_until="domcontentloaded", timeout=30000)
                await page.wait_for_timeout(3000)

                text = await page.inner_text("body")
                html = await page.inner_html("body")
                await browser.close()

            text = text.lower() if text else ""
            html = html.lower() if html else ""

            negative = [
                "no appointment", "no available", "no dates",
                "no appointment available", "there are no appointments",
            ]

            positive = [
                "available appointment", "schedule", "reschedule",
                "consular appointment", "available date", "appointment available",
                "manage appointment",
            ]

            has_negative = any(p in text for p in negative)
            has_positive = any(p in text for p in positive)

            dates = self._extract_dates(text)
            has_calendar = bool(re.search(
                r'class="[^"]*calendar[^"]*"|id="[^"]*calendar[^"]*"',
                html
            ))

            if has_negative:
                return CheckResult("US Travel Docs", name, False, details="Randevu bulunamadı")

            if has_positive and (dates or has_calendar):
                detail = self._build_detail(dates, text)
                return CheckResult("US Travel Docs", name, True, details=detail)

            return CheckResult("US Travel Docs", name, False, details="Randevu bulunamadı")

        except Exception as e:
            return CheckResult("US Travel Docs", name, False, error=str(e))

    def _extract_dates(self, text: str) -> list:
        dates = []
        patterns = [
            r"\b\d{1,2}\s+(Ocak|Şubat|Mart|Nisan|Mayıs|Haziran|Temmuz|Ağustos|Eylül|Ekim|Kasım|Aralık)\s+\d{4}",
            r"\b\d{1,2}\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}",
            r"\b\d{2}\.\d{2}\.\d{4}\b",
            r"\b\d{2}/\d{2}/\d{4}\b",
        ]
        for pat in patterns:
            matches = re.findall(pat, text, re.IGNORECASE)
            for m in matches:
                full = m[0] if isinstance(m, tuple) else m
                if full not in dates:
                    dates.append(full)
        return dates[:5]

    def _build_detail(self, dates: list, text: str) -> str:
        parts = []
        if dates:
            parts.append(f"Uygun tarihler: {', '.join(dates)}")
        if not parts:
            parts.append("Randevu bulundu, sayfayı kontrol edin")
        return " | ".join(parts)
