import os
import logging
import threading

import tkinter
import customtkinter
from tkinter import filedialog
from PIL import ImageGrab

from app.auth import Auth
from app.tables import ExcelReader, DocumentSalesIterator
from app.nalog import Sender

logger = logging.getLogger(__name__)


def get_screen_size() -> tuple:
    return ImageGrab.grab().size


def set_icon(window, filename_without_extension: str) -> None:
    if "Linux" == os.uname().sysname:
        logo = tkinter.PhotoImage(file=f"{filename_without_extension}.gif")
        window.call("wm", "iconphoto", window._w, logo)
    else:
        window.iconbitmap(f"{filename_without_extension}.ico")


class SecondWindow(customtkinter.CTkToplevel):
    def __init__(
        self,
        app: customtkinter.CTk,
        auth: Auth,
        frame: customtkinter.CTkFrame | None = None,
        authorized: bool = False,
    ) -> None:
        super().__init__(app)

        self.authorized = authorized

        self.wm_protocol("WM_DELETE_WINDOW", self.on_closing)
        if not authorized:
            app.withdraw()

        set_icon(app, "assets/wb")

        self.frame = frame
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
            self.destroy()

    def on_closing(self) -> None:
        if self.frame is not None:
            self.frame.toplevel_window = None
        self.destroy()
        if not self.authorized:
            self.app.destroy()


class MyFrame(customtkinter.CTkFrame):
    def __init__(self, master, auth: Auth, **kwargs):
        super().__init__(master, **kwargs)

        self.master = master
        self.auth = auth
        self.toplevel_window = None

        self._width = 140
        self._corner_radius = 0

        self.logo_label = customtkinter.CTkLabel(
            self,
            text="lknpd.nalog.ru\nx\nWildberries",
            font=customtkinter.CTkFont(size=20, weight="bold"),
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.button1 = customtkinter.CTkButton(
            self, text="Авторизация", command=self.open_auth_settings
        )
        self.button1.grid(row=1, column=0, padx=20, pady=10)

        self.button2 = customtkinter.CTkButton(
            self, text="Настройки 2", state=customtkinter.DISABLED
        )

        self.button2.grid(row=2, column=0, padx=20, pady=10)

        self.button3 = customtkinter.CTkButton(
            self, text="Настройки 3", state=customtkinter.DISABLED
        )
        self.button3.grid(row=3, column=0, padx=20, pady=10)

        self.description = customtkinter.CTkLabel(
            self, text="Powered by Ben Puls", text_color="gray"
        )
        self.description.grid(row=5, column=0, padx=20, pady=10)

    def open_auth_settings(self):
        if self.toplevel_window is None:
            self.toplevel_window = SecondWindow(
                self.master, self.auth, self, authorized=True
            )
        else:
            try:
                self.toplevel_window.focus()
            except tkinter.TclError:
                print("Error")
                self.toplevel_window = None


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.toplevel_window = None

        self.screen_size = get_screen_size()
        self.screen_x, self.screen_y = self.screen_size

        self.auth = Auth()

        self.geometry("600x400")
        set_icon(self, "assets/wb")
        self.title("nalog.ru")

        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        if not self.auth.is_auth or self.auth.ask_every_time:
            self.open_toplevel()

        self.sender = Sender(
            login=self.auth.login,
            password=self.auth.password,
        )

        self.frame_sidebar = MyFrame(self, self.auth)
        self.frame_sidebar.grid(row=0, column=0, rowspan=5, sticky="nsew")
        self.frame_sidebar.grid_rowconfigure(4, weight=1)

        self.description = customtkinter.CTkTextbox(self)
        self.description.insert(
            "0.0",
            (
                "Инструкция\n\n"
                "Сначала нажмите на кнопку «Выбрать файл» "
                "затем дождитесь, пока программа прочитает его "
                "и выберет нужные столбцы, а именно: "
                "«Предмет», «Дата продажи» и "
                "«Вайлдберриз реализовал Товар (Пр)»."
                "\n\nПримечание!\nПрограмма выбирает только те строки, "
                "в которых позиция считается успешно реализованной."
                "\n\nПосле успешной обработки данных файла "
                "нажмите на кнопку «Отправить в lknpd.nalog.ru». "
                "Дождитесь окончания отправки."
            ),
        )

        self.description.grid(row=0, column=1, columnspan=2, pady=(0, 0), sticky="nsew")
        self.description.configure(state=customtkinter.DISABLED)

        self.upload_button = customtkinter.CTkButton(
            self, text="Выбрать файл", command=self.open_file
        )
        self.upload_button.grid(row=1, column=1, padx=20, pady=10, sticky="ew")

        self.lknpd_button = customtkinter.CTkButton(
            self,
            text="Отправить в lknpd.nalog.ru",
            command=self.send,
            state=customtkinter.DISABLED,
        )
        self.lknpd_button.grid(row=1, column=2, padx=20, pady=10, sticky="ew")

        self.log = customtkinter.CTkLabel(self, text="Ожидание файла...")
        self.log.grid(row=2, column=1, columnspan=2, pady=(0, 0), sticky="nsew")

        self.progress_bar = customtkinter.CTkProgressBar(self, width=300)
        self.progress_bar.grid(
            row=3, column=1, columnspan=2, pady=(0, 0), sticky="nsew"
        )
        self.progress_bar.set(0)

    def file_task(self, path_to_file: str) -> None:
        reader = ExcelReader(path_to_file, read_only=True)
        self.sales_iterator = DocumentSalesIterator(reader)
        self.progress_bar.stop()
        self.log.configure(text="Файл обработан и готов к отправке.")
        logging.info("File was handled")

    def open_file(self):
        file_path = filedialog.askopenfilename(
            title="Выберите файл",
            filetypes=(("Excel Files", "*.xlsx"),),
        )
        if file_path:
            self.lknpd_button.configure(state=customtkinter.ACTIVE)
            self.log.configure(text=f"{file_path}\nФайл получен. Обрабатываю..")
            logging.info("Start to work with file")
            self.progress_bar.start()

            threading.Thread(
                target=self.file_task, daemon=True, args=[file_path]
            ).start()

        else:
            logging.debug("Choice is canceled")

    def send(self):
        self.log.configure(text="Приступаю к отправке данных")
        self.frame_sidebar.button1.configure(state=customtkinter.DISABLED)
        self.lknpd_button.configure(state=customtkinter.DISABLED)
        self.upload_button.configure(state=customtkinter.DISABLED)
        self.progress_bar.set(0)

        threading.Thread(
            target=self.sender.send_data,
            daemon=True,
            kwargs={
                "iterator": self.sales_iterator,
                "log": self.log,
                "progress_bar": self.progress_bar,
                "upload_button": self.upload_button,
                "sidebar_button": self.frame_sidebar.button1,
            },
        ).start()

    def open_toplevel(self):
        if self.toplevel_window is None:
            self.toplevel_window = SecondWindow(self, self.auth)
            self.toplevel_window.focus()
        else:
            self.toplevel_window.focus()


app = App()
