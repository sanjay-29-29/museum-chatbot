from flask import jsonify
from flask_restful import Resource

class Heartbeat(Resource):
    @staticmethod
    def get():
        return jsonify({"message" : "The server is up and running"})