import importlib

import customtkinter


def run_app(app_path: str) -> None:
    path, app_instance = app_path.split(":")

    module = importlib.import_module(path)
    application: customtkinter.CTk = getattr(module, app_instance)

    application.mainloop()
