# main.py at the project root

import uvicorn
import os
# import pysqlite3
import sys

from dotenv import load_dotenv

load_dotenv()


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, loop="asyncio")