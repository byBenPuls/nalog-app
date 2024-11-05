import customtkinter

from app.utils import WindowsManager


class SettingsWindow(customtkinter.CTkToplevel):
    def __init__(
        self,
        master: customtkinter.CTk,
        manager: WindowsManager,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self.manager = manager

        self.wm_protocol("WM_DELETE_WINDOW", self.on_closing)

        self.geometry("400x300")

        self.title("Настройки")
        self.geometry("300x300")

    def on_closing(self):
        self.manager.close_window(SettingsWindow)
