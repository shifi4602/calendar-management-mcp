import json
import os
import msal
from config import CLIENT_ID, TENANT_ID, SCOPES, TOKEN_CACHE_FILE


def _load_token_cache() -> msal.SerializableTokenCache:
    cache = msal.SerializableTokenCache()
    if os.path.exists(TOKEN_CACHE_FILE):
        with open(TOKEN_CACHE_FILE, "r") as f:
            cache.deserialize(f.read())
    return cache


def _save_token_cache(cache: msal.SerializableTokenCache) -> None:
    if cache.has_state_changed:
        with open(TOKEN_CACHE_FILE, "w") as f:
            f.write(cache.serialize())


class MicrosoftAuthService:
    @staticmethod
    def get_access_token() -> str:
        """
        Returns a valid access token using MSAL Device Code flow.
        On first run the user is prompted to authenticate via browser.
        Subsequent runs reuse the cached token silently.
        """
        cache = _load_token_cache()
        app = msal.PublicClientApplication(
            CLIENT_ID,
            authority=f"https://login.microsoftonline.com/{TENANT_ID}",
            token_cache=cache,
        )

        # Try silent acquisition from the cache first
        accounts = app.get_accounts()
        result = None
        if accounts:
            result = app.acquire_token_silent(SCOPES, account=accounts[0])

        # Fall back to Device Code flow
        if not result:
            flow = app.initiate_device_flow(scopes=SCOPES)
            if "user_code" not in flow:
                raise RuntimeError(f"Failed to create device flow: {json.dumps(flow, indent=2)}")
            print(flow["message"])  # Prints the URL + code for the user
            result = app.acquire_token_by_device_flow(flow)

        _save_token_cache(cache)

        if "access_token" not in result:
            error = result.get("error_description", result.get("error", "Unknown error"))
            raise RuntimeError(f"Could not obtain access token: {error}")

        return result["access_token"]
