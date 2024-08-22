from routes.chatbot_helper.ticket_helper import museumStrength, create_order

async def customResponse(user_state,user_states,user_id, message):
    user_state = user_states.get(user_id, {'awaiting_confirmation': False, 'no_of_tickets': False, 'payment_confirmation': False, 'no_of_tickets_value': 0})

    if user_state['awaiting_confirmation']:
        if 'yes' in message.lower():
            user_states[user_id] = {'awaiting_confirmation': False, 'no_of_tickets': True, 'payment_confirmation': False, 'no_of_tickets_value': 0}
            return {'user':'bot',"type": "message", "message": "How many tickets would you like to book?"}
        
        elif 'no' in message.lower():
            user_states[user_id] = {'awaiting_confirmation': False, 'no_of_tickets': False, 'payment_confirmation': False, 'no_of_tickets_value': 0}
            return {'user':'bot',"type": "message", "message": "Okay, let me know if you need anything else."}
        
        else:
            return {'user':'bot',"type": "message", "message": "Please respond with 'yes' or 'no'."}

    if user_state['no_of_tickets']:
        if 'cancel' in message.lower():
            user_states[user_id] = {'awaiting_confirmation': False, 'no_of_tickets': False, 'payment_confirmation': False, 'no_of_tickets_value': 0}
            return {'user':'bot',"type": "message", "message": "Booking has been cancelled."}
        
        try:
            no_of_tickets = int(message)
            if no_of_tickets <= 0:
                raise ValueError
            
            response = await museumStrength(no_of_tickets, 600)

            if response:
                user_states[user_id] = {'awaiting_confirmation': False, 'no_of_tickets': False, 'payment_confirmation': True, 'no_of_tickets_value': no_of_tickets}
                return {'user':'bot',"type": "message", "message": f"The requested amount of tickets is available. Please enter yes to proceed to payment or 'cancel' to cancel the booking."}
            
            else:
                user_states[user_id] = {'awaiting_confirmation': False, 'no_of_tickets': False, 'payment_confirmation': False, 'no_of_tickets_value': 0}
                return {'user':'bot',"type": "message", "message": "The museum is full right now. Please try again later"}
        
        except ValueError:
            return {'user':'bot',"type": "message", "message": "Please enter a valid number of tickets or type 'cancel' to cancel the booking."}
    
    if user_state['payment_confirmation']:
        if 'cancel' in message.lower():
            user_states[user_id] = {'awaiting_confirmation': False, 'no_of_tickets': False, 'payment_confirmation': False, 'no_of_tickets_value': 0}
            return {'user':'bot',"type": "message", "message": "Booking has been cancelled."}
        
        try:
            if 'yes' in message.lower():
                no_of_tickets = user_state['no_of_tickets_value']
                user_states[user_id] = {'awaiting_confirmation': False, 'no_of_tickets': False, 'payment_confirmation': False, 'no_of_tickets_value': 0}
                data = await create_order(user_id, no_of_tickets)
                print(data)
                return {'user':'bot',"type": "order_id", "message": data}
            else:
                return {'user':'bot',"type":"message","message":"Please enter a valid response"}

        except Exception as e:
            print(e)
            user_states[user_id] = {'awaiting_confirmation': False, 'no_of_tickets': False, 'payment_confirmation': False, 'no_of_tickets_value': 0}
            return {'user':'bot','type': 'message', 'message': 'Unexpected error has happened'}
