import uvicorn
import os

PORT = int(os.getenv("AUTH_PORT", 8002))

if __name__ == "__main__":
    uvicorn.run("src.routes:app", host="0.0.0.0", port=PORT)
