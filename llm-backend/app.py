from fastapi import FastAPI, Body, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import transformers
import torch
from transformers import AutoTokenizer
from time import time
import ngrok

app = FastAPI()

class ValidateRequest(BaseModel):
    user_id: str
    message: str
    system_message: str

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True, 
    allow_methods=["*"], 
    allow_headers=["*"], 
)

model = "/kaggle/input/llama-3/transformers/8b-chat-hf/1"

tokenizer = AutoTokenizer.from_pretrained(model)

pipeline = transformers.pipeline(
    "text-generation",
    model=model,
    torch_dtype=torch.float16,
    device_map="auto"
)

ngrok.set_auth_token("2dVBJw5G2bExzQ41keUUDtC0U8K_7zn55apnGM8YJ3RNsfznb")
listener = ngrok.forward("127.0.0.1:8000", authtoken_from_env=True, domain="glowing-polite-porpoise.ngrok-free.app")

conversation_history = {}

def query_model(system_message, user_id, user_message, temperature=0.7, max_length=1024):
    start_time = time()
    user_message = "Question: " + user_message + " Answer:"

    if user_id not in conversation_history:
        conversation_history[user_id] = []
    conversation_history[user_id].append({"role": "user", "content": user_message})

    conversation_history[user_id] = conversation_history[user_id][-3:]

    prompt = [{"role": "system", "content": system_message}] + conversation_history[user_id]

    prompt_text = pipeline.tokenizer.apply_chat_template(
        prompt,
        tokenize=False, 
        add_generation_prompt=True
    )

    terminators = [
        pipeline.tokenizer.eos_token_id,
        pipeline.tokenizer.convert_tokens_to_ids("<|eot_id|>")
    ]
    sequences = pipeline(
        prompt_text,
        do_sample=True,
        top_p=0.9,
        temperature=temperature,
        eos_token_id=terminators,
        max_new_tokens=max_length,
        return_full_text=False,
        pad_token_id=pipeline.model.config.eos_token_id
    )
    answer = sequences[0]['generated_text']

    conversation_history[user_id].append({"role": "assistant", "content": answer})

    return answer

@app.post('/message')
async def message(request: ValidateRequest):
    try:
        user_id = request.user_id
        user_message = request.message
        system_message = request.system_message
        response = query_model(system_message, user_id, user_message)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))