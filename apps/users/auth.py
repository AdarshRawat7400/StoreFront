# 👆 We're continuing from the steps above. Append this to your webappexample/views.py file.
# 📁 webappexample/views.py -----

from authlib.integrations.django_client import OAuth
from django.conf import settings



oauth = OAuth()

oauth.register(
    "auth0",
    client_id=settings.SOCIAL_AUTH_AUTH0_KEY,
    client_secret=settings.SOCIAL_AUTH_AUTH0_SECRET,
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f"https://{settings.SOCIAL_AUTH_AUTH0_DOMAIN}/.well-known/openid-configuration",
)