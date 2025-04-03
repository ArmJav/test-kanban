from dotenv import load_dotenv
from pathlib import Path
import os

# Явно указываем путь к .env (опционально)
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

# Получаем значение с проверкой
if (DATABASE_URL := os.getenv("DATABASE_URL")) is None:
    raise ValueError("DATABASE_URL не установлен")

if (SECRET_KEY := os.getenv("SECRET_KEY")) is None:
    raise ValueError("SECRET_KEY не установлен")

if (ADMIN_ROLE := os.getenv("ADMIN_ROLE")) is None:
    raise ValueError("ADMIN_ROLE не установлен")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

