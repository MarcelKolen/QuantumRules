from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator, OriginValidator
from django.urls import path

from game.consumers import GameConsumer, ItemConsumer

application = ProtocolTypeRouter({
    # (http->django views is added by default)

    # Construction to only allow websocket connections from the pre-approved hosts.
    # The approved hosts are listed in the settings in settings.py
    'websocket': AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                [
                    path('game/<gameID>/', GameConsumer),
                    path('item/<itemID>/', ItemConsumer),
                ]
            )
        )
    )
})