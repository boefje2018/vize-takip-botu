from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class CheckResult:
    service: str
    center: str
    has_slot: bool
    details: Optional[str] = None
    error: Optional[str] = None


class BaseScraper(ABC):
    def __init__(self, config: dict):
        self.config = config
        self.centers = config.get("centers", [])

    @abstractmethod
    async def check(self, center: dict) -> CheckResult:
        ...
