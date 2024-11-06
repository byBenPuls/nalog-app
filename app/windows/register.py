import customtkinter as ctk

from app.auth import license_is_valid
from app.utils import WindowsManager, Settings
from app.utils.utils import _on_key_release
from app.elements import disable_buttons, enable_buttons


class RegisterWindow(ctk.CTkToplevel):
    def __init__(
        self, app: ctk.CTk, settings: Settings, manager: WindowsManager, **kwargs
    ) -> None:
        super().__init__(app)
        self.app = app
        self.settings = settings
        self.manager = manager

        app.withdraw()

        self.bind_all("<Key>", _on_key_release, "+")

        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        self.title("Регистрация продукта")
        self.geometry("500x350")
        self.resizable(False, False)

        self.label = ctk.CTkLabel(self, text="Введите регистрационный ключ:")
        self.label.grid(row=0, column=0, padx=(20, 0), pady=(0, 0), sticky="s")

        self.textbox = ctk.CTkTextbox(self, width=250)
        self.textbox.bind("<KeyRelease>", self.on_text_change)
        self.textbox.grid(
            row=1, column=0, columnspan=2, padx=(20, 20), pady=(0, 0), sticky="nsew"
        )
        self.textbox.focus()

        self.on_text_change()
        self.button = ctk.CTkButton(self, text="Продолжить", command=self.to_main)
        disable_buttons(self.button)
        self.button.grid(row=2, column=0, padx=(50, 0))

        self.state_ = ctk.CTkLabel(self, text="")
        self.state_.grid(row=2, column=1, padx=(20, 0), sticky="w")

        self.wm_protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_text_change(self, *args) -> None:
        text = self.textbox.get("1.0", "end-1c").replace(" ", "")
        if text:
            self.state_.configure(text="Введённый ключ некорректен", text_color="red")
            if len(text) == 666 and license_is_valid(text):
                self.state_.configure(
                    text="Ключ успешно активирован", text_color="green"
                )
                self.settings["meta"]["license"] = text

                enable_buttons(self.button)

    def on_closing(self) -> None:
        self.manager.close_window(RegisterWindow)
        self.app.destroy()

    def to_main(self) -> None:
        self.manager.close_window(RegisterWindow)
        self.app.deiconify()
