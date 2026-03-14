from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # Gelen ws://.../ws/room/<oda_id>/ isteklerini SignalingConsumer'a yönlendir
    re_path(r'ws/room/(?P<room_name>[\w-]+)/$', consumers.SignalingConsumer.as_asgi()),
]