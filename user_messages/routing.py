# Import the re_path function from Django's urls module. This function is used to define URL patterns with regular expressions.
from django.urls import re_path

# Import the consumers module from the current package. This module contains the WebSocket consumers for your application.
from . import consumers

# Define the WebSocket URL patterns. This is a list of routes that Django will use to route incoming WebSocket connections.
websocket_urlpatterns = [
    # Each route is defined using the re_path function. The first argument is a regular expression that matches the URL.
    # In this case, the URL is expected to be in the format 'ws/notification/<room_name>/', where <room_name> is a word character (\w).
    # The second argument is the consumer that will handle connections to this URL. In this case, it's the as_asgi() application instance of the NotificationConsumer.
    re_path(r'ws/notification/(?P<room_name>\w+)/$', consumers.NotificationConsumer.as_asgi()),
]