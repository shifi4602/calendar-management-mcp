import httpx
from config import CLIENT_ID, CLIENT_SECRET, TENANT_ID, AUTH_URL


class MicrosoftAuthService:
    @staticmethod
    async def get_access_token() -> str:
        """ Fetches the OAuth2 access token for Microsoft Graph API. """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                AUTH_URL,
                data={
                    'client_id': CLIENT_ID,
                    'client_secret': CLIENT_SECRET,
                    'grant_type': 'client_credentials',
                    'scope': 'https://graph.microsoft.com/.default',
                },
            )
            response.raise_for_status()  # Raise exception for non-2xx responses
            token_data = response.json()
            return token_data['access_token']
