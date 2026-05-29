import logging
import os

from dotenv import load_dotenv

load_dotenv()

from emptystream import app


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    port = int(os.getenv("PORT", "5000"))

    app.run(port=port)
