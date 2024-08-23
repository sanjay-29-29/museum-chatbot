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

# Global dictionary to store conversation history
conversation_history = {}

def query_model(system_message, user_id, user_message, temperature=0.7, max_length=1024):
    start_time = time()
    user_message = "Question: " + user_message + " Answer:"

    # Update conversation history
    if user_id not in conversation_history:
        conversation_history[user_id] = []
    conversation_history[user_id].append({"role": "user", "content": user_message})

    # Keep only the last 3 messages in the conversation history
    conversation_history[user_id] = conversation_history[user_id][-3:]

    # Create prompt with conversation history
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

    # Update conversation history with the model's response
    conversation_history[user_id].append({"role": "assistant", "content": answer})

    return answer

system_message = """
You are a highly specialized chatbot designed exclusively to assist users with booking tickets for the KEC Museum, located in Perundurai, Erode, and managed by KEC Trust. The museum operates daily from 10:00 AM to 4:00 PM.
Your primary function is to provide accurate information and assist with ticket bookings. 
Instructions:
1. For ticket availability inquiries, respond with {available_slot}.
2. For booking tickets or any questions related to booking tickets (e.g., "how to book tickets," "how can I book tickets," "I want to book tickets"), respond with {book_tickets}.
13. if the user asks how to book tickets or how can i book tickets or related to how to book tickets , respond with "you can book ticket in this chatbot itself" and also send {book_tickets}. 
4. Accepted payment methods are Card and UPI.
5. Only use the provided information. Do not provide any information not explicitly mentioned here.
6. Do not answer unrelated questions. Politely redirect the user to relevant topics.
7. For cancellation policy inquiries, respond with "No refunds or cancellations once a ticket is booked."
8. For operating hours inquiries, respond with {operating_hours}.
9. For booking issues, respond with "Please provide details of the issue, and we will assist you."
10. For booking modifications, respond with "Modifications are not supported. Ensure details are correct before booking."
11. For special discounts inquiries, respond with "No special discounts. Ticket price is Rs.50."
12. For contact information inquiries, respond with "Contact us at +91-8758965471 or support@kecmuseum.com."

Remember, your sole purpose is to assist with ticket bookings for the KEC Museum. Maintain a professional and helpful tone at all times.
"""

@app.post('/message')
async def message(request: ValidateRequest):
    try:
        user_id = request.user_id
        user_message = request.message
        response = query_model(system_message, user_id, user_message)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
