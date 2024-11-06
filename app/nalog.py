import asyncio
import logging
import threading
from dataclasses import dataclass
import datetime
import tkinter.messagebox
from typing import Iterable

import tkinter
from moy_nalog import MoyNalog
from customtkinter import CTkProgressBar, CTkLabel, CTkButton

from app.auth import Nalog
from app.tables import DocumentSalesIterator, Sale
from app.elements import enable_buttons

logger = logging.getLogger(__name__)


@dataclass
class SenderResult:
    count_of_attempts: int
    successful_attempts: int

    bad_requests: list[dict["str", Exception | Sale]]
    elements: dict


class Sender:
    def __init__(self, nalog: Nalog, cooldown_in_seconds: int = 3) -> None:
        self.cooldown: int = cooldown_in_seconds

        self.nalog: MoyNalog = nalog.get_instance()

        self.bad_requests: list = []

    async def add_income(
        self, name: str, amount: int | float, date: datetime.datetime
    ) -> None:
        await asyncio.sleep(self.cooldown)
        # await self.nalog.add_income(name=name, amount=amount, date=date)

    def handle_exception(self, exc: Exception, item) -> None:
        try:
            raise exc
        except Exception:
            logger.error(f"\nItem: {item}\n", exc_info=True)
        error = {"exception": exc, "item": item}

        self.bad_requests.append(error)

    def update_log_and_progress_bar(
        self,
        log: CTkLabel,
        progress_bar: CTkProgressBar,
        from_: str | int,
        to: str | int,
    ) -> None:
        base_text = "Отправляю данные!"
        modified_ = f"{base_text} ({from_}/{to})"

        log.configure(text=modified_)
        progress_bar.set(int(from_) / int(to))

    def handle_results(self, results: SenderResult) -> None:
        if results.successful_attempts == results.count_of_attempts:
            return

        message = (
            f"{results.count_of_attempts - results.successful_attempts} "
            f"из {results.count_of_attempts} "
            "чеков не были сформированы\n"
            "Подробные данные о непереданных позициях находятся в лог-файле программы, "
            "вы можете попробовать отправить их самостоятельно, или повторить отправку\n"
            "Хотите попробовать отправить ещё раз?"
        )
        question = tkinter.messagebox.askretrycancel(
            title="Данные не были до конца переданы",
            message=message,
        )
        iterators = [[tuple(i.values())[1] for i in results.bad_requests]]
        if question:
            threading.Thread(
                target=self.send_data,
                kwargs={
                    "iterators": iterators,
                    **results.elements,
                },
                daemon=True,
            ).start()

    def send_data(
        self,
        iterators: Iterable[DocumentSalesIterator | Iterable],
        log: CTkLabel,
        progress_bar: CTkProgressBar,
        upload_button: CTkButton,
        sidebar_button: CTkButton,
        settings_button: CTkButton,
    ) -> tuple[int, int]:
        iterator = tuple(i for i in iterators)
        length = 0
        for i in iterators:
            for k in i:
                length += 1

        successful_attempts = 0
        for iterator in iterators:
            for count, item in enumerate(iterator, start=1):
                self.update_log_and_progress_bar(
                    log=log, progress_bar=progress_bar, from_=count, to=length
                )
                try:
                    asyncio.run(
                        self.add_income(
                            name=item.item, amount=item.price, date=item.date
                        )
                    )
                    successful_attempts += 1
                except Exception as ex:
                    self.handle_exception(ex, item)

        progress_bar.set(0)

        log.configure(text="Данные успешно переданы!")

        enable_buttons(upload_button, sidebar_button, settings_button)

        bad_requests = tuple(self.bad_requests)
        self.bad_requests = []

        self.handle_results(
            SenderResult(
                count_of_attempts=length,
                successful_attempts=successful_attempts,
                bad_requests=bad_requests,
                elements={
                    "log": log,
                    "progress_bar": progress_bar,
                    "upload_button": upload_button,
                    "sidebar_button": sidebar_button,
                },
            )
        )
