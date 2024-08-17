import datetime
from typing import Optional, Dict
from prisma import Prisma
import base64
from flask import request, jsonify, make_response
from io import BytesIO
from flask_restful import Resource
import pyqrcode 
import asyncio
import png 

class GenerateQRCode(Resource):
    @staticmethod
    def post():
        data: Optional[Dict] = request.get_json()

        try:
            quantity: int = data['quantity']
        except:
            return jsonify({"message" : "please specify no of ticket"})
        try:
            prisma = Prisma() 

            async def create_ticket():
                await prisma.connect()
                id = await prisma.ticket.create(
                    data = {
                        'quantity': quantity,
                        'creation_time': datetime.datetime.utcnow(),
                        'expiry_time' : datetime.datetime.utcnow() + datetime.timedelta(hours=12)
                    }
                )
                return id

            ticket = asyncio.run(create_ticket())
        
            qr = pyqrcode.create(ticket.id)
            buffer = BytesIO()
            qr.png(buffer, scale=5)
            buffer.seek(0)

            img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

            response_data = {
                'id' : ticket.id,
                'quantity' : ticket.quantity,
                'expiry_time' : ticket.expiry_time.isoformat() if isinstance(ticket.expiry_time, datetime.datetime) else ticket.expiry_time,
                'qr_code' : img_base64
            }

            return jsonify(response_data)
        
        except Exception as e:
            print(e)
            return jsonify({"message": str(e)})

        
