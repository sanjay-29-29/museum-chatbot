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

user_histories = {}

def query_model(system_message, user_message, history, temperature=0.7, max_length=1024):
    start_time = time()
    user_message = "Question: " + user_message + " Answer:"
    messages = history + [
        {"role": "user", "content": user_message},
    ]
    prompt = pipeline.tokenizer.apply_chat_template(
        messages, 
        tokenize=False, 
        add_generation_prompt=True
    )
    terminators = [
        pipeline.tokenizer.eos_token_id,
        pipeline.tokenizer.convert_tokens_to_ids("<|eot_id|>")
    ]
    sequences = pipeline(
        prompt,
        do_sample=True,
        top_p=0.9,
        temperature=temperature,
        eos_token_id=terminators,
        max_new_tokens=max_length,
        return_full_text=False,
        pad_token_id=pipeline.model.config.eos_token_id
    )
    answer = sequences[0]['generated_text']

    return answer, messages

system_message = """
You are a chatbot designed to assist users with booking tickets for the KEC Museum, located in Perundurai, Erode and is managed by KEC Trust. The museum operates daily from 10:00 AM to 4:00 PM.
When users inquire about the availability of tickets, respond with {available_slot}. The mueseum is known for rich collection of artifacts of viking era. If users request to book tickets or ask 
questions related to booking, respond with {book_tickets}. If the user specifies the number of ticket while booking respond with {book_ticket,no_of_tickets} where no_of_tickets is the tickets user 
specified.Only use the provided information to answer all user queries and do not halucinate. 
"""

@app.post('/message')
async def message(request: ValidateRequest):
    try:
        global user_histories
        user_id = request.user_id
        user_message = request.message
        history = user_histories.get(user_id, [{"role": "system", "content": system_message}])
        response, updated_history = query_model(system_message, user_message, history)
        user_histories[user_id] = updated_history
        user_histories = user_histories[-3:]
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))