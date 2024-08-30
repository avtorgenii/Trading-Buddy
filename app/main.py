from os import getenv
from dotenv import load_dotenv
import uvicorn

if __name__ == "__main__":
    load_dotenv()

    from app.server import app

    port = int(getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
