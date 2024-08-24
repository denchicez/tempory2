import logging

import uvicorn
from routes import app

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S", level=logging.INFO)

tasks = []

if __name__ == '__main__':
    uvicorn.run(app, port=8001)
