import datetime
from typing import Optional, Dict
from prisma import Prisma
import base64
from flask import request, jsonify
from io import BytesIO
from flask_restful import Resource
import pyqrcode 
import asyncio
import png 

class GenerateQRCode(Resource):
    @staticmethod
    def get():
        data: Optional[Dict] = request.get_json()

        try:
            person: int = data['person']
        except:
            return jsonify({"message" : "please specify no of ticket"})
        
        prisma = Prisma() 
        async def create_ticket():
            await prisma.connect()
            id = await prisma.ticket.create(
                data = {
                    'person': person,
                    'Validity': datetime.datetime.utcnow(),
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
            'id': ticket.id,
            'person': ticket.person,
            'Validity': ticket.Validity.isoformat() if isinstance(ticket.Validity, datetime.datetime) else ticket.Validity,
            'qr_code': img_base64
        }
        return jsonify(response_data)

        
