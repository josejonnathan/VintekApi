from django.db import models
from api_operations.models import CustomUser, Product
# This line imports the chain function from the itertools module. The chain function is used to combine multiple iterables into a single iterable.
from itertools import chain
# This line imports the Q object from Django's models module. Q objects are used to create complex database queries.
from django.db.models import Q


# This is the definition of the Message model.
class Message(models.Model):
    # These lines define the sender, recipient, and product fields of the Message model. Each of these fields is a foreign key field, which means it is a reference to another model.
    sender = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='sent_messages')
    recipient = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='received_messages')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)

    # This line defines the message field of the Message model. This field is a text field, which means it can contain an arbitrary amount of text.
    message = models.TextField()

    # This line defines the timestamp field of the Message model. This field is a datetime field, and it is automatically set to the current date and time whenever a new Message instance is created.
    timestamp = models.DateTimeField(auto_now_add=True)

    # This line defines the reply_to field of the Message model. This field is a foreign key field that references the Message model itself. This is used to create a hierarchy of messages, where each message can be a reply to another message.
    reply_to = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, related_name='replies')

    # This is the string representation method for the Message model. It returns a string that represents the Message instance.
    def __str__(self):
        return f'{self.sender.username} - {self.recipient.username}'

    # This is a static method that retrieves all conversations for a given user.
    @staticmethod
    def get_conversations(user):
        # An empty list is initialized to store the conversations.
        conversations = []

        # The distinct senders of messages to the user are retrieved.
        senders = Message.objects.filter(recipient=user).values_list('sender', flat=True).distinct()

        # The distinct recipients of messages from the user are retrieved.
        recipients = Message.objects.filter(sender=user).values_list('recipient', flat=True).distinct()

        # The distinct users who have either sent messages to or received messages from the user are retrieved.
        other_users = CustomUser.objects.filter(id__in=chain(senders, recipients))

        # For each other user, the conversation between the user and the other user is retrieved and added to the conversations list.
        for other_user in other_users:
            conversation = Message.get_conversation(user, other_user)
            conversations.append({'other_user': other_user, 'conversation': conversation})

        # The conversations list is returned.
        return conversations

    # This is a static method that retrieves the conversation between two users.
    @staticmethod
    def get_conversation(user1, user2):
        # The messages between the two users are retrieved.
        messages = Message.objects.filter(Q(sender=user1, recipient=user2) | Q(sender=user2, recipient=user1))

        # The messages are ordered by timestamp and returned.
        return messages.order_by('timestamp')