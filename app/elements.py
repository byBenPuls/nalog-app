from typing import Iterable

import customtkinter as ctk


def disable_buttons(buttons: Iterable[ctk.CTkButton]) -> None:
    for button in buttons:
        button.configure(state=ctk.DISABLED)


def enable_buttons(buttons: Iterable[ctk.CTkButton]) -> None:
    for button in buttons:
        button.configure(state=ctk.ACTIVE)
