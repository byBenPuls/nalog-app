import customtkinter

from app.utils import WindowsManager, Settings
from app.elements import FloatSpinbox


class SettingsWindow(customtkinter.CTkToplevel):
    def __init__(
        self,
        master: customtkinter.CTk,
        settings: Settings,
        manager: WindowsManager,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self.manager = manager
        self.settings = settings

        self.grid_rowconfigure((0, 1, 2), weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.wm_protocol("WM_DELETE_WINDOW", self.on_closing)

        self.geometry("300x300")

        self.title("Настройки")

        self.frame = customtkinter.CTkFrame(self)
        self.frame.grid(row=0, column=0, sticky="nsew")

        self.label = customtkinter.CTkLabel(
            self.frame, text="Интервал между отправкой новых отчётов"
        )
        self.label.grid(row=0, column=0, padx=(20, 20), sticky="ew")

        self.spinbox_1 = FloatSpinbox(self.frame, width=150, step_size=1)
        self.spinbox_1.grid(row=1, column=0, pady=(30, 30), sticky="ew")
        self.spinbox_1.set(self.settings["cooldown"])

        self.button = customtkinter.CTkButton(
            self, text="Сохранить", command=self.save_settings
        )
        self.button.grid(row=1, column=0, sticky="ew")

    def on_closing(self):
        self.manager.close_window(SettingsWindow)

    def save_settings(self):
        if cooldown := self.spinbox_1.get():
            self.settings["cooldown"] = cooldown
        self.on_closing()
