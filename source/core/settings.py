import os
import pathlib
from urllib.parse import quote

from pydantic import BaseSettings

BASE_DIR: str = str(pathlib.Path(__file__).parent.parent.parent)


class Settings(BaseSettings):
    db_host=""
    db_port=""
    db_user=""
    db_password=""
    db_name=""
    prod_mode: bool = False

    tg_bot_token: str

    class Config:
        _env_file = os.path.join(BASE_DIR, '.env')
        if os.path.exists(_env_file):
            env_file = _env_file

    log_file: str = os.path.join(BASE_DIR, 'story.log')


settings = Settings()
