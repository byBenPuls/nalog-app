import os

import tkinter
import customtkinter as ctk
from PIL import ImageGrab


def get_screen_size() -> tuple:
    return ImageGrab.grab().size


def set_icon(window, filename_without_extension: str) -> None:
    if "Linux" == os.uname().sysname:
        logo = tkinter.PhotoImage(file=f"{filename_without_extension}.gif")
        window.call("wm", "iconphoto", window._w, logo)
    else:
        window.iconbitmap(f"{filename_without_extension}.ico")


class WindowsManager:
    def __init__(self) -> None:
        self._windows: dict = {}

    def open_window(self, window_class: ctk.CTkToplevel, *args, **kwargs) -> None:
        name = window_class.__name__

        if name not in self._windows:
            self._windows[name] = window_class(*args, manager=self, **kwargs)
        else:
            self._windows[name].focus()

    def close_window(self, window_class: ctk.CTkToplevel) -> None:
        name = window_class.__name__

        if name not in self._windows:
            return
        self._windows[name].destroy()
        del self._windows[name]
