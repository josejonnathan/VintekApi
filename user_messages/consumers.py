# Import the necessary modules
import json
from channels.generic.websocket import AsyncWebsocketConsumer
import logging

# Define a class that inherits from AsyncWebsocketConsumer
class NotificationConsumer(AsyncWebsocketConsumer):
    # Define an asynchronous method to establish a WebSocket connection
    async def connect(self):
        # Get the room name from the URL route
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        # Define the group name for the room
        self.room_group_name = 'messages_%s' % self.room_name

        # Add the current channel to the group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # Accept the WebSocket connection
        await self.accept()

    # Define an asynchronous method to handle disconnection
    async def disconnect(self, close_code):
        # Remove the current channel from the group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
         # Log a message

        )
        logging.info(f'WebSocket disconnected, close code: {close_code}')

        
        # Also remove the current channel from the notifications group
        await self.channel_layer.group_discard(
            'notifications',
            self.channel_name
        )

    # Define an asynchronous method to handle chat messages
    async def chat_message(self, event):
        # Extract necessary information from the event
        sender_username = event['sender_username']
        product_name = event['product_name']
        message = event.get('message')
        timestamp = event.get('timestamp')  # Get the timestamp from the event

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'sender_username': sender_username,
            'product_name': product_name,
            'message': message,
            'timestamp': timestamp,  # Include the timestamp in the data
        }))

    # Define an asynchronous method to handle chat replies
    async def chat_reply(self, event):
        # Import necessary models
        from api_operations.models import Product, CustomUser
        from .models import Message

        # Extract necessary information from the event
        reply_message = event.get('message')
        sender_username = event.get('sender_username')
        product_name = event.get('product_name')
        timestamp = event.get('timestamp')
        reply_to_id = event.get('reply_to_id')  # Get the ID of the original message

        # Get the sender and product from the database
        sender = CustomUser.objects.get(username=sender_username)
        product = Product.objects.get(name=product_name)

        # Get the original message from the database
        reply_to = Message.objects.get(id=reply_to_id)

        # Save the reply to the database
        reply = Message.objects.create(
            message=reply_message,
            sender=sender,
            product=product,
            timestamp=timestamp,
            reply_to=reply_to,  # Set the reply_to field to the original message
        )

        # Send a message over the WebSocket connection to update the frontend
        await self.send(text_data=json.dumps({
            'message': reply_message,
            'sender_username': sender_username,
            'product_name': product_name,
            'timestamp': str(reply.timestamp),
        }))
        