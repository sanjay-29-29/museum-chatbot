import torch
from typing import Optional, Dict
import os
import random
from flask import request, jsonify, make_response
from routes.model.nltk_utils import bag_of_words, tokenize
from flask_restful import Resource
from routes.model.model import NeuralNet
from dotenv import load_dotenv
import json

def initialize_model():
    with open(os.getenv('INTENTS_PATH'), 'r') as json_data:
        intents = json.load(json_data)
    load_dotenv()
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    data = torch.load(os.getenv('MODEL_PATH'))
    input_size = data["input_size"]
    hidden_size = data["hidden_size"]
    output_size = data["output_size"]
    all_words = data['all_words']
    tags = data['tags']
    model_state = data["model_state"]
    model = NeuralNet(input_size, hidden_size, output_size).to(device)
    model.load_state_dict(model_state)
    model.eval()
    return model, device, data, all_words, tags, intents

class Chatbot(Resource):
    def __init__(self):
        self.model, self.device, self.data, self.all_words, self.tags, self.intents = initialize_model()
    
    def post(self):
        data: Optional[Dict] = request.get_json()

        try:
            message: str = data['message']
        except:
            return jsonify({"message" : "please enter a message"})
        
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
                    return jsonify({"message": random.choice(intent['responses'])})
        
        return jsonify("Ask me relevant questions")
                
        