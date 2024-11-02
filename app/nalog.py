import asyncio
import datetime

from moy_nalog import MoyNalog


class Sender:
    def __init__(self, login: str, password: str,
                 cooldown_in_seconds: int = 3) -> None:
        self.cooldown = cooldown_in_seconds

        self.nalog = self._init_moy_nalog(login, password)

    def _init_moy_nalog(self, login, password):
        return MoyNalog(login, password)

    async def add_income(self, name: str, amount: int | float,
                         date: datetime.datetime):
        await asyncio.sleep(self.cooldown)
        await self.nalog.add_income(name=name, amount=amount,
                                    date=date)
    