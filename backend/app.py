from flask import Flask
from flask_restful import Api
from routes.Heartbeat import Heartbeat
from routes.GenerateQRCode import GenerateQRCode

app = Flask(__name__)

rest_api = Api(app, errors=Flask.errorhandler)

rest_api.add_resource(Heartbeat, '/heartbeat')
rest_api.add_resource(GenerateQRCode,'/qr')

if __name__ == '__main__':
    app.run(debug=True)