import customtkinter as ctk


def disable_button(button: ctk.CTkButton) -> None:
    button.configure(state=ctk.DISABLED)


def enable_button(button: ctk.CTkButton) -> None:
    button.configure(state=ctk.ACTIVE)
