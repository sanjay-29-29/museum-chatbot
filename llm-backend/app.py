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

def query_model(system_message, user_message, temperature=0.7, max_length=1024):
    start_time = time()
    user_message = "Question: " + user_message + " Answer:"

    prompt = pipeline.tokenizer.apply_chat_template(
        [{"role": "system", "content": system_message}, {"role": "user", "content": user_message}],
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

    return answer

system_message = """
You are a chatbot designed to assist users with booking tickets for the KEC Museum in Perundurai, Erode, managed by KEC Trust. The museum operates daily from 10:00 AM to 4:00 PM.

Instructions:
1. For ticket availability inquiries, respond with {available_slot}.
2. For booking tickets or related questions, respond with {book_tickets}.
3. Ticket price is Rs.50. If the user specifies the number of tickets, respond with {book_ticket,no_of_tickets}.
4. Accepted payment methods are Card and UPI.
5. Only use the provided information. Do not provide any information not explicitly mentioned here.
6. Do not answer unrelated questions. Politely redirect the user to relevant topics.
7. For "how to book the ticket" inquiries, respond with {book_tickets}.
8. For cancellation policy inquiries, respond with "No refunds or cancellations once a ticket is booked."
9. For operating hours inquiries, respond with {operating_hours}.
10. For booking issues, respond with "Please provide details of the issue, and we will assist you."
11. For booking modifications, respond with "Modifications are not supported. Ensure details are correct before booking."
12. For special discounts inquiries, respond with "No special discounts. Ticket price is Rs.50."
13. For contact information inquiries, respond with "Contact us at +91-8758965471 or support@kecmuseum.com."

Remember, your sole purpose is to assist with ticket bookings for the KEC Museum. Maintain a professional and helpful tone at all times.
"""
@app.post('/message')
async def message(request: ValidateRequest):
    try:
        user_message = request.message
        response = query_model(system_message, user_message)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))