import customtkinter as ctk


class WindowsManager:
    def __init__(self) -> None:
        self._windows: dict = {}

    def open_window(self, window_class: ctk.CTkToplevel, *args, **kwargs) -> None:
        name = window_class.__name__

        if name not in self._windows:
            self._windows[name] = window_class(*args, manager=self, **kwargs)
            self._windows[name].grab_set()  # make modal window strict!!!
        else:
            self._windows[name].focus()

    def close_window(self, window_class: ctk.CTkToplevel) -> None:
        name = window_class.__name__

        if name not in self._windows:
            return
        self._windows[name].destroy()
        del self._windows[name]

    def is_open(self, window_class: ctk.CTkToplevel) -> bool:
        return window_class.__name__ in self._windows
