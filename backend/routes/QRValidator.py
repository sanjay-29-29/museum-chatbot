from flask_restful import Resource
from prisma import Prisma
import asyncio
from typing import Optional, Dict
from flask import request, jsonify, Response

class QRValidatorIn(Resource):
    def post(self):
        data: Optional[Dict] = request.get_json()

        try:
            print(data)
            ticket_id: str = data['ticket_id']
        except KeyError:
            return jsonify({"type":"error","message": "TicketId not found"})

        async def getQr():
            try:
                prisma = Prisma()    
                await prisma.connect()
                ticket = await prisma.ticket.find_unique(where={
                    "id" : ticket_id
                })
                return ticket
            except:
                return None
        
        loop = asyncio.new_event_loop()
        ticket = loop.run_until_complete(getQr())
        
        if(ticket is None):
            return Response(jsonify({"error": "The given ticketId is not valid"}), 400)
        
        if(ticket.quantity == ticket.person_in):
            return Response(jsonify({"error": "already reached max limit"}), 400)
                 
        async def updateQr():
            try:
                prisma = Prisma()
                await prisma.connect()
                await prisma.ticket.update(
                    where={
                        "id": ticket_id
                    },
                    data={
                        "person_in": {
                            "increment": 1
                        }
                    }
                )
            except:
                return Response(jsonify({"error": "error in updation of data"}), 400)
            
        loop.run_until_complete(updateQr())
            
        return Response(jsonify({'status':"success"}), 200)

class QRValidatorOut(Resource):
    def post(self):
        data: Optional[Dict] = request.get_json()

        try:
            ticket_id: str = data['ticket_id']
            print(data)
        except KeyError:
            return Response(jsonify({"type":"error","message": "TicketId not found"}), 400)

        async def getQr():
            try:
                prisma = Prisma()    
                await prisma.connect()
                ticket = await prisma.ticket.find_unique_or_raise(where={
                    "id" : ticket_id
                })
                return ticket
            except:
                return None
        
        loop = asyncio.new_event_loop()
        ticket = loop.run_until_complete(getQr())
        
        if(ticket is None):
            return Response(jsonify({"error": "The given ticketId is not valid"}), 400)
        
        if(ticket.person_out == ticket.person_in):
            return Response(jsonify({"error": "already reached max limit"}), 400)
         
        async def updateQr():
            try:
                prisma = Prisma()
                await prisma.connect()
                await prisma.ticket.update(
                    where={
                        "id": ticket_id
                    },
                    data={
                        "person_out": {
                            "increment": 1
                        }
                    }
                )
            except:
                return Response(jsonify({"error": "error in updation of data"}), 400)
            
        loop.run_until_complete(updateQr())
            
        return Response(jsonify({'status':"success"}), 200)