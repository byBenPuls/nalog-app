import logging
import threading

import tkinter
import tkinter.messagebox
import customtkinter
from tkinter import filedialog

from app.auth import Auth, Nalog, license_is_valid
from app.tables import ExcelReader, DocumentSalesIterator
from app.nalog import Sender
from app.windows.auth import SecondWindow
from app.windows.settings import SettingsWindow
from app.windows.register import RegisterWindow
from app.utils.settings import Settings
from app.utils import set_icon, get_screen_size, WindowsManager, get_app_version
from app.elements import enable_buttons, disable_buttons

logger = logging.getLogger(__name__)


class MyFrame(customtkinter.CTkFrame):
    def __init__(self, master, manager: WindowsManager, auth: Auth, **kwargs):
        super().__init__(master, **kwargs)

        self.master = master
        self.manager = manager
        self.auth = auth

        self._width = 140
        self._corner_radius = 0

        self.logo_label = customtkinter.CTkLabel(
            self,
            text="lknpd.nalog.ru\nx\nWildberries",
            font=customtkinter.CTkFont(size=20, weight="bold"),
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.button1 = customtkinter.CTkButton(
            self, text="lknpd.nalog.ru", command=self.open_auth_settings
        )
        self.button1.grid(row=1, column=0, padx=20, pady=10)

        self.button2 = customtkinter.CTkButton(
            self,
            text="Настройки 2",
            command=self.open_settings_window,
        )

        self.button2.grid(row=2, column=0, padx=20, pady=10)

        self.button3 = customtkinter.CTkButton(
            self, text="Настройки 3", state=customtkinter.DISABLED
        )
        self.button3.grid(row=3, column=0, padx=20, pady=10)

        self.description = customtkinter.CTkLabel(
            self,
            text=f"Powered by Ben Puls\n{get_app_version()} version",
            text_color="gray",
        )
        self.description.grid(row=5, column=0, padx=20, pady=10)

    def open_auth_settings(self):
        self.manager.open_window(
            SecondWindow,
            app=self.master,
            auth=self.auth,
            nalog=self.master.nalog,
            authorized=True,
        )

    def open_settings_window(self):
        self.manager.open_window(SettingsWindow, self.master, self.master.settings)


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.settings = Settings()
        self.manager = WindowsManager()
        # self.manager.open_window(MonthWindow, number_of_months=[10, 11])
        self.license = self.settings["meta"]["license"]
        if not self.license and not license_is_valid(self.license):
            self.manager.open_window(RegisterWindow, self, self.settings)

        self.wm_protocol("WM_DELETE_WINDOW", self.on_closing)

        self.screen_size = get_screen_size()
        self.screen_x, self.screen_y = self.screen_size

        self.auth = Auth()
        self.nalog = Nalog(self.auth.login, self.auth.password)

        self.geometry("600x400")
        set_icon(self, "assets/wb")
        self.title("nalog.ru")

        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        if not self.auth.is_auth or self.auth.ask_every_time:
            self.open_toplevel()

        self.frame_sidebar = MyFrame(self, manager=self.manager, auth=self.auth)
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
        if not self.auth.is_auth:
            disable_buttons(self.upload_button)

        self.lknpd_button = customtkinter.CTkButton(
            self,
            text="Отправить в lknpd.nalog.ru",
            command=self.send,
            state=customtkinter.DISABLED,
        )
        self.lknpd_button.grid(row=1, column=2, padx=20, pady=10, sticky="ew")

        self.log = customtkinter.CTkLabel(self, text="Ожидание файла...")
        self.log.grid(row=3, column=1, columnspan=2, pady=(0, 0), sticky="nsew")

        self.progress_bar = customtkinter.CTkProgressBar(self, width=300)
        self.progress_bar.grid(
            row=4, column=1, columnspan=2, pady=(0, 0), sticky="nsew"
        )
        self.progress_bar.set(0)

    def file_task(self, paths_to_files: tuple) -> None:
        suffix = "ы" if len(paths_to_files) > 1 else ""
        readers = tuple(ExcelReader(i, read_only=True) for i in paths_to_files)
        self.sales_iterators = tuple(
            DocumentSalesIterator(reader) for reader in readers
        )
        self.progress_bar.stop()
        self.log.configure(
            text=f"Файл{suffix} обработан{suffix} и готов{suffix} к отправке."
        )
        logging.info("File was handled")

    def open_file(self):
        files_paths = filedialog.askopenfilenames(
            title="Выберите один или несколько файлов",
            filetypes=(("Excel Files", "*.xlsx"),),
        )
        if files_paths:
            enable_buttons(self.lknpd_button)
            suffix = "ы" if len(files_paths) > 1 else ""
            logging.info(f"{files_paths}")
            self.log.configure(text=f"Файл{suffix} получен{suffix}. Обрабатываю..")
            logging.info("Start to work with file")
            self.progress_bar.start()

            threading.Thread(
                target=self.file_task, daemon=True, args=[files_paths]
            ).start()

        else:
            logging.debug("Choice is canceled")

    def send(self):
        self.sender = Sender(self.nalog, cooldown_in_seconds=self.settings["cooldown"])

        self.log.configure(text="Приступаю к отправке данных")
        disable_buttons(
            self.frame_sidebar.button1,
            self.frame_sidebar.button2,
            self.lknpd_button,
            self.upload_button,
        )
        self.progress_bar.set(0)

        threading.Thread(
            target=self.sender.send_data,
            daemon=True,
            kwargs={
                "iterators": self.sales_iterators,
                "log": self.log,
                "progress_bar": self.progress_bar,
                "upload_button": self.upload_button,
                "sidebar_button": self.frame_sidebar.button1,
                "settings_button": self.frame_sidebar.button2,
            },
        ).start()

    def open_toplevel(self):
        print(self.manager.is_open(RegisterWindow))
        while not self.manager.is_open(RegisterWindow):
            self.manager.open_window(SecondWindow, self, self.auth, self.nalog)
            break

    def on_closing(self):
        question = tkinter.messagebox.askokcancel(
            title="Подтверждение", message="Вы действительно хотите выйти?"
        )

        if question:
            self.destroy()
