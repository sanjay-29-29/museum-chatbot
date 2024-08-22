import os
from dotenv import load_dotenv
import torch
from routes.model.model import NeuralNet
import json


def initialize_model():
    load_dotenv()
    with open(os.getenv('INTENTS_PATH'), 'r') as json_data:
        intents = json.load(json_data)
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    data = torch.load(os.getenv('MODEL_PATH'), map_location=device)
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
