import os

import dotenv
import uvicorn
from fastapi import FastAPI

from app.routers import status, users

dotenv.load_dotenv(''.join((os.path.abspath(__file__).split('tests')[0], '.env.sample')))


app = FastAPI()
app.include_router(status.router)
app.include_router(users.router)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8003)
