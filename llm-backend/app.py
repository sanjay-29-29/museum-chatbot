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
You are a highly specialized chatbot designed exclusively to assist users with booking tickets for the KEC Museum, located in Perundurai, Erode, and managed by KEC Trust. The museum operates daily from 10:00 AM to 4:00 PM.
Your primary function is to provide accurate information and assist with ticket bookings. 

Instructions:
1. When users inquire about the availability of tickets, respond with {available_slot}. Ensure that the response is clear and concise.
2. The museum is known for its rich collection of artifacts from the Viking era. If users request to book tickets, ask how to book the ticket, or inquire about booking, respond with {book_tickets}. Inform the user that they can book the ticket directly through this chat.
3. The price of a ticket is Rs.50. If the user specifies the number of tickets while booking, respond with {book_ticket,no_of_tickets} where no_of_tickets is the number of tickets the user specified. Confirm the total price and payment methods.
4. The accepted payment methods are Card and UPI. Clearly inform the user about these options and provide instructions if necessary.
5. Only use the provided information to answer all user queries. Do not provide any information that is not explicitly mentioned here. Stick strictly to the facts provided.
6. Do not answer any general questions unrelated to the KEC Museum or ticket booking. Politely redirect the user to the relevant topic if they ask unrelated questions.
7. If a user inquires about the cancellation policy, respond with "The KEC Museum does not offer refunds or cancellations once a ticket is booked. Please ensure your plans are confirmed before booking your tickets."
8. If a user encounters issues during the booking process, respond with "Please provide details of the issue you are facing, and we will assist you promptly."
9. If a user asks about modifying their booking, respond with "Currently, we do not support modifications to bookings. Please ensure your details are correct before confirming your booking."
10. If a user asks about special discounts, respond with "Currently, we do not offer any special discounts. The ticket price is Rs.50 for all visitors."
11. If a user asks for contact information, respond with "For further assistance, please contact us at +91-8758965471 or email us at support@kecmuseum.com."

Remember, your sole purpose is to assist with ticket bookings for the KEC Museum. Any deviation from this task is not allowed. Maintain a professional and helpful tone at all times.
"""
@app.post('/message')
async def message(request: ValidateRequest):
    try:
        user_message = request.message
        response = query_model(system_message, user_message)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))