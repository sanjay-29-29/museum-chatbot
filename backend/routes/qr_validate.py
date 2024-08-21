from prisma import Prisma
from models.model import QRRequest
from datetime import datetime
import pytz
from fastapi import HTTPException

async def qr_validate_in(request: QRRequest):
    data = request.dict()
    try:
        ticket_id: str = data['ticket_id']
    except KeyError:
        raise HTTPException(status_code=404, detail="TicketId not found")
    
    prisma = Prisma()    
    await prisma.connect()
    ticket = await prisma.ticket.find_unique(where={
        "id": ticket_id
    })
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    current_time = datetime.now(pytz.utc)
    
    if ticket.expiry_time < current_time:
        raise HTTPException(status_code=404, detail="The QR code has expired")
        
    if ticket.quantity == ticket.person_in:
        raise HTTPException(status_code=404, detail="Already reached max limit")
    
    try:
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
        raise HTTPException(status_code=400, detail="Error in updating data")
    
    return {'status': "success"}

async def qr_validate_out(request: QRRequest):
    data = request.dict()
    try:
        ticket_id: str = data['ticket_id']
    except KeyError:
        raise HTTPException(status_code=404, detail="TicketId not found")
    
    prisma = Prisma()    
    await prisma.connect()
    try:
        ticket = await prisma.ticket.find_unique_or_raise(where={
            "id" : ticket_id
        })
    except:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    if(ticket.person_out == ticket.person_in):
        raise HTTPException(status_code=404, detail="already reached max limit")
    try:
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
         raise HTTPException(status_code=404, detail="error in updation")
    
    return {'status': "success"}