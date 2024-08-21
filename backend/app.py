from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from routes.chatbot import Chatbot
from routes.qr_validate import qr_validate_in, qr_validate_out
from routes.validate import Validate

from models.model import ValidateRequest, ChatRequest, QRRequest

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
    chatbot_instance = Chatbot()
    return await chatbot_instance.post(request)

@app.post("/validate")
async def validate(request: ValidateRequest):
    validate  = Validate()
    return await validate.post(request)

@app.post('/qr/in')
async def qr_in(request: QRRequest):
    return await qr_validate_in(request)

@app.post('/qr/out')
async def qr_out(request: QRRequest):
    return await qr_validate_out(request)