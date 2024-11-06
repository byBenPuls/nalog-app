import logging
import json
import base64

from httpx import Client, HTTPStatusError
from moy_nalog import MoyNalog

from app.utils import guid

logger = logging.getLogger(__name__)


class Auth:
    def __init__(self) -> None:
        logger.debug("Auth successfully initialized")

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
        return bool(self.open_nalog_auth())

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


def license_is_valid(key: str, id_: str = guid()) -> bool:
    with Client() as client:
        try:
            res = client.post(
                "https://wb.benpuls.ru/token", json={"token": key, "id": id_}
            )
            res.raise_for_status()

            return True
        except HTTPStatusError:
            return False


class Nalog:
    def __init__(self, login: str, password: str) -> None:
        self.__nalog_instance = MoyNalog(login, password)

    def update_instance(self, instance: MoyNalog) -> None:
        self.__nalog_instance = instance

    def get_instance(self) -> MoyNalog:
        return self.__nalog_instance
