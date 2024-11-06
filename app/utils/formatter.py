import os
import json
from pathlib import Path


settings_pattern = {"cooldown": 3.0, "meta": {"license": ""}}


class CannotFormatDataError(Exception):
    pass


class Formatter:
    def __init__(self):
        self.settings_location = "data/settings.json"

    def _format_file(self, data: str, pattern: dict) -> None:
        try:
            print(data)
            json_data = json.loads(data)

            if json_data.keys() == pattern.keys() and {
                type(key) for key in json_data.values()
            } == {type(key) for key in pattern.values()}:
                return json_data
            return pattern
        except json.JSONDecodeError:
            return pattern

    def format_settings(self) -> None:
        path = Path(self.settings_location)
        if not path.is_file():
            os.mkdir("data")
            with open(path, "w+") as f:
                f.write(json.dumps(settings_pattern, indent=4))
            return
        with open(path, "r") as f:
            data = f.read()
        serialized = self._format_file(data, settings_pattern)
        with open(path, "w") as f:
            f.write(json.dumps(serialized, indent=4))


Formatter().format_settings()
