import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Configuration values for Microsoft OAuth2
CLIENT_ID = os.getenv('MICROSOFT_CLIENT_ID')
CLIENT_SECRET = os.getenv('MICROSOFT_CLIENT_SECRET')
TENANT_ID = os.getenv('MICROSOFT_TENANT_ID')
AUTH_URL = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"
MICROSOFT_API_URL = "https://graph.microsoft.com/v1.0/me/events"


# config.py
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

MICROSOFT_API_URL = os.getenv("MICROSOFT_API_URL")
