from pathlib import Path
import requests
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from models.model import ChatRequest
from routes.chatbot_helper.chatbot_helper import checkBookWithQnty, customResponse
from routes.chatbot_helper.ticket_helper import museumStrength, ticketsAvailable
from routes.model.load_model import initialize_model

user_states = {}


class Chatbot:
    def __init__(self):
        self.model, self.device, self.data, self.all_words, self.tags, self.intents = (
            initialize_model()
        )

    async def post(self, request: ChatRequest):
        print(request)
        data = request.dict()

        try:
            message: str = data["message"]
            user_id: str = data["user_id"]
            prompt: str = data["prompt"]
        except KeyError:
            return {"type": "message", "message": "please enter a message and user_id"}

        user_state = user_states.get(
            user_id,
            {
                "awaiting_confirmation": False,
                "no_of_tickets": False,
                "payment_confirmation": False,
                "no_of_tickets_value": 0,
            },
        )

        try:
            path = Path("./prompts/" + prompt + ".txt")
            with open(path, "r", encoding="UTF-8") as f:
                system_message = f.read()
        except FileNotFoundError:
            return {"type": "message", "message": "the provided prompt is not available"}

        custom_response = await customResponse(
            user_state, user_states, user_id, message
        )

        if custom_response:
            return custom_response

        try:
            data = requests.post(
                "https://glowing-polite-porpoise.ngrok-free.app/message",
                json={
                    "message": message,
                    "user_id": user_id,
                    "system_message": system_message,
                },
            )
            print(data.status_code)
            if data.status_code == 200:
                json_data = data.json()
                checkTicketinResponse = checkBookWithQnty(json_data["response"])
                if checkTicketinResponse:
                    response = await museumStrength(checkTicketinResponse, 600)
                    if response:
                        user_states[user_id] = {
                            "awaiting_confirmation": False,
                            "no_of_tickets": False,
                            "payment_confirmation": True,
                            "no_of_tickets_value": checkTicketinResponse,
                        }
                    else:
                        return {
                            "user": "bot",
                            "type": "message",
                            "message": "The is {prompt} full right now. Please try again later".format(prompt=prompt),
                        }
                if "{book_tickets}" in json_data["response"]:
                    json_data["response"] = str(json_data["response"]).replace(
                        "{book_tickets}", ""
                    )
                    user_states[user_id] = {
                        "awaiting_confirmation": True,
                        "no_of_tickets": False,
                        "payment_confirmation": False,
                    }
                    # todo prompt llm properly
                    return {
                        "user": "bot",
                        "type": "message",
                        "message": json_data["response"]
                        + "To continue with the booking process please respond with 'yes' to continue or 'no' to cancel the process.",
                    }

                if "{available_slot}" in json_data["response"]:
                    ticket_qty = await ticketsAvailable(750)
                    # todo ticket_available with number specified
                    response = str(json_data["response"])
                    if ticket_qty:
                        print(response)
                        response = response.replace("{available_slot}", str(ticket_qty))
                        return {"user": "bot", "type": "message", "message": response}
                    else:
                        return {"user": "bot", "type": "message", "message": response}
                else:
                    return {
                        "user": "bot",
                        "type": "message",
                        "message": json_data["response"],
                    }
            else:
                return JSONResponse(
                    status_code=400, content={"error": "no response from llm"}
                )
        except Exception as e:
            print(e)
            return HTTPException(
                status_code=400, detail={"error": "Internal Server Error"}
            )
