import logging
import os

from dotenv import load_dotenv

from emptystream import create_app

load_dotenv()

app = create_app()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app.run(port=int(os.getenv("PORT", "5000")))
