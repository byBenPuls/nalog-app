import logging
import json
import base64

logger = logging.getLogger(__name__)


class Auth:
    def __init__(self) -> None:
        logger.debug("Auth successfully initialized")
        self.__nalog = self.open_nalog_auth()
        self.__data = self.__nalog if self.__nalog is not None else {}

    def write_nalog_data(self) -> None:
        pass

    def open_nalog_auth(self) -> dict:
        logger.debug("Trying to open resources/pass.json")
        with open("resources/pass.json", "r") as f:
            encoded_data = f.read()
            if encoded_data == "":
                return None

        json_text = base64.b64decode(json.loads(encoded_data.encode())["pass"]).decode()
        data = json.loads(json_text)
        return data

    def execute_nalog_auth(
        self, login: str, password: str, ask_every_time: bool
    ) -> None:
        data = json.dumps({"login": login, "password": password, "ask": ask_every_time})
        encoded_data = base64.b64encode(data.encode()).decode()
        with open("resources/pass.json", "w") as file:
            file.write(json.dumps({"pass": encoded_data}))

    def execute_app_auth(self) -> None:
        pass

    @property
    def is_auth(self):
        return self.__data != {}

    @property
    def ask_every_time(self):
        file = self.open_nalog_auth()
        if file is not None:
            return file.get("ask")

    @property
    def login(self):
        file = self.open_nalog_auth()
        if file is not None:
            return file.get("login")

    @property
    def password(self):
        file = self.open_nalog_auth()
        if file is not None:
            return file.get("password")
