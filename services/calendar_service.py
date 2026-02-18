import httpx
from datetime import datetime, timedelta
from typing import List
from config import MICROSOFT_API_URL
from models.event_model import Event
from models.time_slot_model import TimeSlot


class CalendarService:

    @staticmethod
    async def get_access_token() -> str:
        """ Fetches the OAuth2 access token for Microsoft Graph API. """
        # Implement token fetching logic
        pass

    @staticmethod
    async def get_workweek_dates(start_date: datetime) -> (datetime, datetime):
        """ Given a start date, return the start and end of the workweek (Monday to Friday). """
        # Find the start of the week (Monday)
        start_of_week = start_date - timedelta(days=start_date.weekday())
        # Assuming workweek ends on Friday
        end_of_week = start_of_week + timedelta(days=4)
        return start_of_week, end_of_week

    @staticmethod
    async def read_events_for_workweek(start_date: datetime) -> List[dict]:
        """ Fetches calendar events for the workweek based on the start date. """
        start_of_week, end_of_week = await CalendarService.get_workweek_dates(start_date)

        # Convert to ISO format strings
        start_of_week = start_of_week.isoformat()
        end_of_week = end_of_week.isoformat()

        access_token = await CalendarService.get_access_token()

        params = {
            '$startDateTime': start_of_week,
            '$endDateTime': end_of_week,
            '$orderby': 'start/dateTime',
        }

        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
        }

        # Microsoft Graph API for events
        api_url = MICROSOFT_API_URL

        async with httpx.AsyncClient() as client:
            response = await client.get(api_url, params=params, headers=headers)
            response.raise_for_status()  # Raise exception for non-2xx responses
            return response.json().get('value', [])

    @staticmethod
    async def create_event(event: Event) -> dict:
        """ Creates a new event on Microsoft Graph. """
        access_token = await CalendarService.get_access_token()

        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
        }

        # Microsoft Graph API for creating an event
        api_url = MICROSOFT_API_URL

        async with httpx.AsyncClient() as client:
            response = await client.post(api_url, json=event.to_dict(), headers=headers)
            response.raise_for_status()
            return response.json()

    @staticmethod
    async def update_event(event: Event) -> dict:
        """ Updates an existing event on Microsoft Graph. """
        if not event.event_id:
            raise ValueError("Event ID is required for updating an event.")

        access_token = await CalendarService.get_access_token()

        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
        }

        # Microsoft Graph API for updating an event
        api_url = MICROSOFT_API_URL

        async with httpx.AsyncClient() as client:
            response = await client.patch(api_url, json=event.to_dict(), headers=headers)
            response.raise_for_status()
            return response.json()

    @staticmethod
    async def delete_event(event_id: str) -> dict:
        """ Deletes an event from Microsoft Graph. """
        access_token = await CalendarService.get_access_token()

        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
        }

        # Microsoft Graph API for deleting an event
        api_url = f"https://graph.microsoft.com/v1.0/me/events/{event_id}"

        async with httpx.AsyncClient() as client:
            response = await client.delete(api_url, headers=headers)
            response.raise_for_status()
            return {'status': 'deleted', 'id': event_id}

    @staticmethod
    def find_available_slots(events: List[dict], required_duration: timedelta) -> List[TimeSlot]:
        """ Finds available slots between existing events based on the required duration. """
        available_slots = []

        # Sort events by start time
        events_sorted = sorted(events, key=lambda x: x['start']['dateTime'])

        # Check for available slot before the first event
        if events_sorted:
            first_event_start = datetime.fromisoformat(events_sorted[0]['start']['dateTime'])
            now = datetime.now()

            # Consider available time before the first event
            if first_event_start > now:
                gap = first_event_start - now
                if gap >= required_duration:
                    available_slots.append(TimeSlot(now, first_event_start))

            # Check gaps between consecutive events
            for i in range(1, len(events_sorted)):
                current_event_end = datetime.fromisoformat(events_sorted[i - 1]['end']['dateTime'])
                next_event_start = datetime.fromisoformat(events_sorted[i]['start']['dateTime'])

                # Check if there is enough space between events for the required duration
                gap = next_event_start - current_event_end
                if gap >= required_duration:
                    available_slots.append(TimeSlot(current_event_end, next_event_start))

            # Check if there's space after the last event
            last_event_end = datetime.fromisoformat(events_sorted[-1]['end']['dateTime'])
            available_slots.append(TimeSlot(last_event_end, last_event_end + required_duration))

        return available_slots

    @staticmethod
    async def read_events(from_date: datetime, to_date: datetime) -> List[dict]:
        """ Fetches calendar events from Microsoft Graph API within a date range. """
        access_token = await CalendarService.get_access_token()

        params = {
            '$startDateTime': from_date.isoformat(),
            '$endDateTime': to_date.isoformat(),
            '$orderby': 'start/dateTime',
        }

        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
        }

        # Microsoft Graph API for events
        api_url = "https://graph.microsoft.com/v1.0/me/events"

        async with httpx.AsyncClient() as client:
            response = await client.get(api_url, params=params, headers=headers)
            response.raise_for_status()  # Raise exception for non-2xx responses
            return response.json().get('value', [])

