from tkinter import messagebox
import customtkinter as ctk

from app.utils import set_icon
from app.utils.manager import WindowsManager
from app.elements import execute_event_on_closing

months_in_russian = {
    1: "Январь",
    2: "Февраль",
    3: "Март",
    4: "Апрель",
    5: "Май",
    6: "Июнь",
    7: "Июль",
    8: "Август",
    9: "Сентябрь",
    10: "Октябрь",
    11: "Ноябрь",
    12: "Декабрь",
}


class MonthWindow(ctk.CTkToplevel):
    def __init__(
        self, *args, number_of_months: list, manager: WindowsManager, **kwargs
    ):
        super().__init__(*args, **kwargs)
        set_icon(self)

        execute_event_on_closing(self, self.on_closing)

        self.number_of_months = number_of_months
        self.manager = manager

        self.title("Выбор месяца")
        self.geometry("350x200")

        self.rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.label = ctk.CTkLabel(
            self,
            text=(
                "В таблицах было обнаружено 2 месяца\n"
                "Выберите, какой месяц будет выгружен:"
            ),
            justify="center",
        )
        self.label.grid(row=0, column=0, columnspan=2, pady=20)

        self.options = ctk.CTkOptionMenu(
            self,
            values=[months_in_russian[i] for i in self.number_of_months],
            corner_radius=4,
        )
        self.options.grid(row=1, column=0)

        self.save_button = ctk.CTkButton(self, text="Выбрать")
        self.save_button.grid(row=2, column=0, pady=(0, 15))

    def on_closing(self):
        message = messagebox.askokcancel(
            "Предупреждение",
            "Если вы не выберете нужный месяц,"
            " то программа не выгрузит данные на lknpd.nalog.ru"
            ", и операция будет прервана",
        )
        if message:
            self.manager.close_window(MonthWindow)
