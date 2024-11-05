import customtkinter

from app.auth import Auth
from app.utils import set_icon, WindowsManager


class SecondWindow(customtkinter.CTkToplevel):
    def __init__(
        self,
        app: customtkinter.CTk,
        auth: Auth,
        manager: WindowsManager,
        authorized: bool = False,
    ) -> None:
        super().__init__(app)

        self.manager = manager
        self.authorized = authorized

        self.wm_protocol("WM_DELETE_WINDOW", self.on_closing)
        if not authorized:
            app.withdraw()

        set_icon(app, "assets/wb")

        self.app = app
        self.auth = auth

        self.title("Авторизация nalog.ru")
        self.geometry("300x300")

        self.label_username = customtkinter.CTkLabel(self, text="Имя пользователя")
        self.label_username.pack(pady=(20, 0))

        self.entry_username = customtkinter.CTkEntry(self)
        if self.auth.login is not None:
            self.entry_username.insert(0, self.auth.login)
        self.entry_username.pack(pady=(0, 10))

        self.label_password = customtkinter.CTkLabel(self, text="Пароль")
        self.label_password.pack(pady=(10, 0))

        self.entry_password = customtkinter.CTkEntry(self, show="*")
        if self.auth.login is not None:
            self.entry_password.insert(0, self.auth.password)
        self.entry_password.pack(pady=(0, 10))

        self.button_login = customtkinter.CTkButton(
            self, text="Войти", command=self.login
        )
        self.button_login.pack(pady=(15, 0))

        checkbox_variable = customtkinter.BooleanVar(value=self.auth.ask_every_time)

        self.checkbox = customtkinter.CTkCheckBox(
            self, text="Спрашивать при открытии", variable=checkbox_variable
        )
        self.checkbox.pack(pady=(0, 0))

    def login(self):
        login = self.entry_username.get()
        password = self.entry_password.get()
        checkbox = bool(self.checkbox.get())

        if login != "" and password != "":
            self.auth.execute_nalog_auth(login, password, checkbox)

            self.app.deiconify()
            self.manager.close_window(SecondWindow)

    def on_closing(self) -> None:
        self.manager.close_window(SecondWindow)
        if not self.authorized:
            self.app.destroy()
