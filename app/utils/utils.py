import sys
import subprocess
import configparser
import platform

import tkinter
from PIL import ImageGrab


def get_app_version() -> str:
    config = configparser.ConfigParser(allow_no_value=True, delimiters=("=", ":"))
    config.read("pyproject.toml")

    try:
        version = config["tool.poetry"]["version"]
        return version.replace('"', "")
    except KeyError:
        print("Version not found in pyproject.toml.")
        return None


def get_screen_size() -> tuple:
    return ImageGrab.grab().size


def set_icon(window, filename_without_extension: str = "assets/wb") -> None:
    if "Linux" == platform.system():
        logo = tkinter.PhotoImage(file=f"{filename_without_extension}.gif")
        window.call("wm", "iconphoto", window._w, logo)
    else:
        window.iconbitmap(f"{filename_without_extension}.ico")


def run(cmd):
    try:
        return subprocess.run(
            cmd, shell=True, capture_output=True, check=True, encoding="utf-8"
        ).stdout.strip()
    except Exception:
        return None


def guid():
    if sys.platform == "darwin":
        return run(
            "ioreg -d2 -c IOPlatformExpertDevice | awk -F\\\" '/IOPlatformUUID/{print $(NF-1)}'",
        )

    if sys.platform == "win32" or sys.platform == "cygwin" or sys.platform == "msys":
        return run("wmic csproduct get uuid").split("\n")[2].strip()

    if sys.platform.startswith("linux"):
        return run("cat /var/lib/dbus/machine-id") or run("cat /etc/machine-id")

    if sys.platform.startswith("openbsd") or sys.platform.startswith("freebsd"):
        return run("cat /etc/hostid") or run("kenv -q smbios.system.uuid")


def _on_key_release(event):
    ctrl = (event.state & 0x4) != 0
    if event.keycode == 88 and ctrl and event.keysym.lower() != "x":
        event.widget.event_generate("<<Cut>>")

    if event.keycode == 86 and ctrl and event.keysym.lower() != "v":
        event.widget.event_generate("<<Paste>>")

    if event.keycode == 67 and ctrl and event.keysym.lower() != "c":
        event.widget.event_generate("<<Copy>>")
