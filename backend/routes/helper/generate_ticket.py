from prisma import Prisma
import asyncio
import base64
import pyqrcode 
import datetime
from weasyprint import HTML
from io import BytesIO

def generateTicket(quantity, max):
    try:
        prisma = Prisma() 

        async def create_ticket():
            await prisma.connect()
            
            total_in_out = await prisma.ticket.find_many()
            in_total = 0
            out_total = 0

            for i in total_in_out:
                in_total += i.person_in
                out_total += i.person_out

            if(in_total-out_total > max):
                return [False,"The museum is full right now"]

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
        
        html_content = f"""
        <html>
        <head>
            <style>
                body {{
                    text-align: center;
                    font-family: Arial, sans-serif;
                }}
                .ticket {{
                    border: 1px solid #000;
                    padding: 20px;
                    display: inline-block;
                }}
                .qr-code {{
                    margin: 20px 0;
                }}
            </style>
        </head>
        <body>
            <div class="ticket">
                <h1>Ticket</h1>
                <div class="qr-code">
                    <img src="data:image/png;base64,{img_base64}" alt="QR Code">
                </div>
                <p>Quantity: {quantity}</p>
                <p>Expiry: {ticket.expiry_time.strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
        </body>
        </html>
        """
        
        pdf = HTML(string=html_content).write_pdf()
        
        pdf_base64 = base64.b64encode(pdf).decode('utf-8')
        
        return [True, pdf_base64]
        
    except Exception as e:
        print(f"Error: {e}")
        return [False, 'error']