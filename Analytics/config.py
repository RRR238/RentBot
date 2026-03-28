import os
from dotenv import load_dotenv

load_dotenv()

CONN_STRING = os.getenv("connection_string")