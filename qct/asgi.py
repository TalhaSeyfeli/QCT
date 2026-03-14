import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import qct_app.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'qct.settings')

django_asgi_app = get_asgi_application()



application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            qct_app.routing.websocket_urlpatterns
        )
    ),
})
