from os import getenv
import uvicorn

from app.server import app


if __name__ == "__main__":
    port = int(getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)


