from source.core.settings import Settings
from source.db.db import DB

settings = Settings()
db = DB(settings.db_name, settings.db_user, settings.db_password, settings.db_host, settings.db_port)