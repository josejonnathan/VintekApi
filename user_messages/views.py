from .serializers import MessageSerializer
from rest_framework import generics, permissions
from django.db.models import  Q
from .models import Message
# Import the get_channel_layer function from Django Channels
from channels.layers import get_channel_layer

# Import the async_to_sync function from the asgiref.sync module
from asgiref.sync import async_to_sync

# Import the get_user_model function from Django's authentication module
from django.contrib.auth import get_user_model
import logging
logger = logging.getLogger(__name__)
from api_operations.models import Product, CustomUser
from datetime import datetime
from django.utils import timezone
import threading
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib import messages

# Define a function to send a message via WebSocket
def send_message(message):
    # Get the channel layer
    channel_layer = get_channel_layer()

    # Send the message to the group
    async_to_sync(channel_layer.group_send)(
        f'messages_{message.recipient.id}',
        {
            'type': 'chat.message',
            'sender_username': message.sender.username,
            'product_name': message.product.name,  # Include product name
            'message': message.message,  # Send only the message text
            'timestamp': message.timestamp.strftime("%m/%d/%Y, %H:%M:%S"),  # Send the timestamp as a string
        }
    )

    # Log the sent message
    logger.info(f"Sent message to WebSocket: {message.message} at {message.timestamp.strftime('%m/%d/%Y, %H:%M:%S')}")

# Get the user model
User = get_user_model()

# Define a view to list and create messages
class MessageListView(generics.ListCreateAPIView):
    # Specify the serializer class
    serializer_class = MessageSerializer

    # Specify the permission classes
    permission_classes = [permissions.IsAuthenticated]
    
    # Define the queryset
    def get_queryset(self):
        # If the user is not authenticated, return an empty queryset
        if not self.request.user.is_authenticated:
            return Message.objects.none()

        # Otherwise, return messages where the user is either the sender or the recipient, ordered by 'reply_to' and 'timestamp'
        return Message.objects.filter(Q(sender=self.request.user) | Q(recipient=self.request.user)).order_by('reply_to', 'timestamp')
        
    # Define the create operation
    def perform_create(self, serializer):
        # Get the sender ID from the request data
        sender_id = self.request.data.get('sender')

        # Get the sender user instance
        sender = User.objects.get(id=sender_id)

        # Save the message and get the instance
        message = serializer.save(sender=sender)

        # Print a message indicating that the message was created
        print(f'Created Message: {message}')
        
        # Call the send_message function in a new thread
        threading.Thread(target=send_message, args=(message,)).start()

# Define a view to retrieve, update and delete a message
class MessageDetailView(generics.RetrieveUpdateDestroyAPIView):
    # Specify the serializer class
    serializer_class = MessageSerializer

    # Specify the permission classes
    permission_classes = [permissions.IsAuthenticated]

    # Define the queryset
    def get_queryset(self):
        # Get the user from the request
        user = self.request.user

        # Get the product from the query parameters
        product = self.request.query_params.get('product', None)

        # Return messages where the user is either the sender or the recipient and the product is the specified product
        return Message.objects.filter(Q(sender=user) | Q(recipient=user), product=product)

# Define a view to create a reply
class ReplyCreateView(generics.CreateAPIView):
    # Specify the serializer class
    serializer_class = MessageSerializer

    # Specify the permission classes
    permission_classes = [permissions.IsAuthenticated]

    # Define the create operation
    def perform_create(self, serializer):
        # Get the recipient ID from the request data
        recipient_id = self.request.data.get('recipient')

        # Print the recipient ID
        print(f" Replay :Recipient ID: {recipient_id}") 

        # Get the recipient user instance
        recipient = CustomUser.objects.get(id=recipient_id)

        # Get the product ID from the request data and convert it to an integer
        product_id = int(self.request.data.get('product'))

        # Get the product instance
        product = Product.objects.get(id=product_id)

        # Get the message text from the request data
        message_text = self.request.data.get('message')

        # Get the timestamp from the request data
        timestamp = self.request.data.get('timestamp')

        # Set the timestamp to the current time
        timestamp = timezone.now()

        # Get the reply_to ID from the request data
        reply_to_id = self.request.data.get('reply_to')

        # If there is a reply_to ID, get the message instance, otherwise set reply_to to None
        reply_to = Message.objects.get(id=reply_to_id) if reply_to_id else None

        # Save the message and get the instance
        message = serializer.save(sender=self.request.user, recipient=recipient, product=product, message=message_text, timestamp=timestamp, reply_to=reply_to)
        
        # Call the send_message function in a new thread
        threading.Thread(target=send_message, args=(message,)).start()

# Define a view to delete a conversation
class DeleteConversationView(APIView):
    # Specify the permission classes
    permission_classes = [permissions.IsAuthenticated]

    # Define the delete operation
    def delete(self, request, product_id):
        # Get the conversation
        conversation = Message.objects.filter(product_id=product_id)

        # If the conversation does not exist, return a 404 error
        if not conversation.exists():
            messages.error(request, 'Conversation does not exist')
            return Response({'detail': 'Conversation does not exist'}, status=status.HTTP_404_NOT_FOUND)

        # If the user is not the sender or the recipient of the first message in the conversation, return a 403 error
        elif not request.user in [conversation.first().sender, conversation.first().recipient]:
            messages.error(request, 'You do not have permission to delete this conversation')
            return Response({'detail': 'You do not have permission to delete this conversation'}, status=status.HTTP_403_FORBIDDEN)

        # Otherwise, delete the conversation and return a success message
        else:
            conversation.delete()
            messages.success(request, 'Conversation deleted successfully')
            return Response({'detail': 'Conversation deleted successfully'}, status=status.HTTP_200_OK)

    # Define the get operation
    def get(self, request, *args, **kwargs):
        # Return a 405 error because the GET method is not allowed
        return Response({'detail': 'Invalid method'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)