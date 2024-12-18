# from fastapi import FastAPI, Response

# app = FastAPI()


# @app.post("/cookie-and-object/")
# def create_cookie(response: Response):
#     response.set_cookie(key="fakesession", value="fake-cookie-session-value")
#     return {"message": "Come to the dark side, we have cookies"}

from dotenv import load_dotenv
import os

load_dotenv()

print(os.getenv("DATABASE_URL"))