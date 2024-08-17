from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from routes.Heartbeat import Heartbeat
from routes.GenerateQRCode import GenerateQRCode
from routes.Chatbot import Chatbot

app = Flask(__name__)
CORS(app)

rest_api = Api(app, errors=Flask.errorhandler)

rest_api.add_resource(Heartbeat, '/heartbeat')
rest_api.add_resource(GenerateQRCode,'/qr')
rest_api.add_resource(Chatbot, '/chatbot')

if __name__ == '__main__':
    app.run(debug=True)