import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mixjam.settings")
django.setup()

from channels.routing import ProtocolTypeRouter, URLRouter

import api.routing

from .middleware import TokenAuthMiddleware

application = ProtocolTypeRouter({
    'websocket': TokenAuthMiddleware(
        URLRouter(
            api.routing.websocket_urlpatterns
        )
    )
})
