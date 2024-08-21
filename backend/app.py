from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from models.model import ValidateRequest, ChatRequest, QRRequest
import time

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/heartbeat")
def read_heartbeat():
    return {"status": "alive"}

@app.post("/chatbot")
async def chatbot(request: ChatRequest):

    return {'type':'message','message':' According to reports . RCB  has the best fanbase of all franchise '}