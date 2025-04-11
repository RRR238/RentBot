from dotenv import load_dotenv
from pathlib import Path
import os

env_path = Path(__file__).resolve().parents[1] / 'Scrapping' / '.env'
load_dotenv(dotenv_path=env_path)

# Use variables like this
CONN_STRING = os.getenv("connection_string")