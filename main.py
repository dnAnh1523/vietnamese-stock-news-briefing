"""Entry point."""

import os

import uvicorn
from dotenv import load_dotenv

load_dotenv()


if __name__ == "__main__":
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("PORT") or os.getenv("API_PORT", "8000"))
    uvicorn.run("api.routes:app", host=host, port=port, reload=False)
