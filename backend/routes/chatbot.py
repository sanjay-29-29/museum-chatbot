from pydantic import BaseModel
import torch
import random
from routes.model.load_model import initialize_model
from routes.model.nltk_utils import bag_of_words, tokenize
from routes.chatbot_helper.chatbot_helper import customResponse
from models.model import ChatRequest

user_states = {}
    
class Chatbot():
    def __init__(self):
        self.model, self.device, self.data, self.all_words, self.tags, self.intents = initialize_model()
    
    async def post(self, request: ChatRequest):
        data = request.dict()

        try:
            message: str = data['message']
            user_id: str = data['user_id']
        except KeyError:
            return {"type":"message","message": "please enter a message and user_id"}
        
        user_state = user_states.get(user_id, {'awaiting_confirmation': False, 'no_of_tickets': False, 'payment_confirmation': False})

        custom_response = await customResponse(user_state, user_states, user_id, message)
        
        if custom_response:
            return custom_response

        sentence = tokenize(message)
        X = bag_of_words(sentence, self.all_words)
        X = X.reshape(1, X.shape[0])
        X = torch.from_numpy(X).to(self.device)

        output = self.model(X)
        _, predicted = torch.max(output, dim=1)

        tag = self.tags[predicted.item()]

        probs = torch.softmax(output, dim=1)
        prob = probs[0][predicted.item()]
        if prob.item() > 0.90:
            for intent in self.intents['intents']:
                if tag == intent["tag"]:
                    if tag == 'book_ticket':
                        user_states[user_id] = {'awaiting_confirmation': True, 'no_of_tickets': False}
                        return {"type":"message","message": f'The ticket price is Rs.50. Please enter "yes" to continue or "no" to cancel the process.'}
                    else:   
                        return {"type":"message","message": random.choice(intent['responses'])}

        return {"type":"message","message": "Ask me relevant questions"}