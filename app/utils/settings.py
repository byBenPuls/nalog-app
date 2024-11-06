import json
from typing import Any


class SettingsDict:
    def __init__(self, data: dict, parent) -> None:
        self.data = data
        self.parent = parent

    def __getitem__(self, key: Any) -> Any:
        return self.data[key]

    def __setitem__(self, key: Any, value: Any) -> None:
        self.data[key] = value

        with open("data/settings.json", "w") as f:
            json.dump(self.parent.settings_data, f, indent=4)


class Settings:
    def __init__(self) -> None:
        self.settings_data = self._get_settings_data()

    def _get_settings_data(self) -> dict:
        with open("data/settings.json", "r") as f:
            return json.load(f)

    def get(self, key: Any, default: None | Any = None):
        try:
            return self[key]
        except KeyError:
            return default

    def __getitem__(self, item: Any) -> Any:
        if isinstance(self.settings_data[item], dict):
            return SettingsDict(self.settings_data[item], self)
        return self.settings_data[item]

    def __setitem__(self, key: Any, value: Any) -> None:
        self.settings_data[key] = value

        with open("data/settings.json", "w") as f:
            json.dump(self.settings_data, f, indent=4)
