import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Configuration values for Microsoft OAuth2
CLIENT_ID = os.getenv('MICROSOFT_CLIENT_ID')
CLIENT_SECRET = os.getenv('MICROSOFT_CLIENT_SECRET')
TENANT_ID = os.getenv('MICROSOFT_TENANT_ID')

# Microsoft Graph API base URL for calendar events
MICROSOFT_API_URL = "https://graph.microsoft.com/v1.0/me/events"

# OAuth scopes required for calendar read/write access
SCOPES = ["Calendars.ReadWrite"]

# File path for persisting the MSAL token cache between runs
TOKEN_CACHE_FILE = "token_cache.json"
