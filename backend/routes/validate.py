from models.model import ValidateRequest
import razorpay
from prisma import Prisma
from routes.chatbot_helper.ticket_helper import generateTicket

class Validate():
    async def post(self, request: ValidateRequest):
        data = request.dict()

        try:
            payment_id: str = data['payment_id']
            order_id: str = data['order_id']
            razor_signature: str = data['razor_signature']

        # except KeyError as e:
        #     print(e)
        #     return {'error':'all the fields are excepted'}
        
        #client = razorpay.Client(auth=())
        
        # try:
        #     client.verify_payment_signature({
        #         'razorpay_order_id': order_id,
        #         'razorpay_payment_id': payment_id,
        #         'razorpay_signature': razor_signature
        #     })

        except Exception as e:
            print(e)
            return {'error':'razor pay validation failed'}
        
        prisma = Prisma()
        await prisma.connect()

        data = await prisma.order.find_unique(where={
            'order_id': order_id
        })

        pdf = await generateTicket(data.quantity)
        return {"type": "content", "message": "success", "pdf": str(pdf)}
        