# Import the os module to interact with the operating system
import os

# Import the get_asgi_application function from django.core.asgi
# This function returns an instance of the ASGI application to be used by the server
from django.core.asgi import get_asgi_application

# Import the ProtocolTypeRouter and URLRouter from channels.routing
# ProtocolTypeRouter is a top-level ASGI application that routes to other ASGI applications based on the protocol type
# URLRouter is an ASGI middleware that routes to ASGI applications based on the URL path
from channels.routing import ProtocolTypeRouter, URLRouter

# Import the routing module from the user_messages app
import user_messages.routing

# Set the default settings module for Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api.settings')

# Create an instance of the ProtocolTypeRouter
# This will route HTTP requests to the ASGI application returned by get_asgi_application
# And WebSocket requests to the ASGI application defined in user_messages.routing.websocket_urlpatterns
application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": URLRouter(
        user_messages.routing.websocket_urlpatterns
    ),
})