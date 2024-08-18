import torch
from typing import Optional, Dict
from routes.model.load_model import initialize_model
from routes.helper.generate_ticket import generateTicket
import random
from flask import request, jsonify
from routes.model.nltk_utils import bag_of_words, tokenize
from flask_restful import Resource

user_states = {}

class Chatbot(Resource):
    def __init__(self):
        self.model, self.device, self.data, self.all_words, self.tags, self.intents = initialize_model()
    
    def post(self):
        data: Optional[Dict] = request.get_json()

        try:
            message: str = data['message']
            user_id: str = data['user_id']
        except KeyError:
            return jsonify({"type":"message","message": "please enter a message and user_id"})
        
        user_state = user_states.get(user_id, {'awaiting_confirmation': False, 'no_of_tickets': False})

        if user_state['awaiting_confirmation']:
            if 'yes' in message.lower():
                user_states[user_id] = {'awaiting_confirmation': False, 'no_of_tickets': True}
                return jsonify({"type":"message","message": "How many tickets would you like to book?"})
            elif 'no' in message.lower():
                user_states[user_id] = {'awaiting_confirmation': False, 'no_of_tickets': False}
                return jsonify({"type":"message","message": "Okay, let me know if you need anything else."})
            else:
                return jsonify({"type":"message","message": "Please respond with 'yes' or 'no'."})

        if user_state['no_of_tickets']:
            if 'cancel' in message.lower():
                user_states[user_id] = {'awaiting_confirmation': False, 'no_of_tickets': False}
                return jsonify({"type":"message","message": "Booking has been cancelled."})
            try:
                no_of_tickets = int(message)
                user_states[user_id] = {'awaiting_confirmation': False, 'no_of_tickets': False}
                response = generateTicket(no_of_tickets,4)
                if(response[0]):
                    return jsonify({"type":"content","message": f"Booking {no_of_tickets} tickets. Thank you!", "pdf":response[1]})
                else:
                    return jsonify({"type":"message","message": "The museum is full right now. Please try again later"})
            except ValueError:
                return jsonify({"type":"message","message": "Please enter a valid number of tickets or type 'cancel' to cancel the booking."})

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
                        return jsonify({"type":"message","message": f'The ticket price is $20. Please enter "yes" to continue or "no" to cancel the process.'})
                    else:   
                        return jsonify({"type":"message","message": random.choice(intent['responses'])})

        return jsonify({"type":"message","message": "Ask me relevant questions"})

                        
        