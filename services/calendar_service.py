import httpx
from datetime import datetime, timedelta
from typing import List
from config import MICROSOFT_API_URL
from models.event_model import Event
from models.time_slot_model import TimeSlot
from services.auth_service import MicrosoftAuthService


class CalendarService:

    @staticmethod
    def get_access_token() -> str:
        """Returns a valid Microsoft Graph access token."""
        return MicrosoftAuthService.get_access_token()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    async def get_workweek_dates(start_date: datetime) -> (datetime, datetime):
        """Given a start date, return the start and end of the workweek (Monday–Friday)."""
        start_of_week = start_date - timedelta(days=start_date.weekday())
        end_of_week = start_of_week + timedelta(days=4)
        return start_of_week, end_of_week

    # ------------------------------------------------------------------
    # Existing tools (fixed)
    # ------------------------------------------------------------------

    @staticmethod
    async def read_events_for_workweek(start_date: datetime) -> List[dict]:
        """Fetches calendar events for the workweek based on the start date."""
        start_of_week, end_of_week = await CalendarService.get_workweek_dates(start_date)

        access_token = CalendarService.get_access_token()
        params = {
            '$startDateTime': start_of_week.isoformat(),
            '$endDateTime': end_of_week.isoformat(),
            '$orderby': 'start/dateTime',
        }
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(MICROSOFT_API_URL, params=params, headers=headers)
            response.raise_for_status()
            return response.json().get('value', [])

    @staticmethod
    async def create_event(event: Event) -> dict:
        """Creates a new event on Microsoft Graph."""
        access_token = CalendarService.get_access_token()
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(MICROSOFT_API_URL, json=event.to_dict(), headers=headers)
            response.raise_for_status()
            return response.json()

    @staticmethod
    async def update_event(event: Event) -> dict:
        """Updates an existing event on Microsoft Graph."""
        if not event.event_id:
            raise ValueError("Event ID is required for updating an event.")

        access_token = CalendarService.get_access_token()
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
        }
        url = f"{MICROSOFT_API_URL}/{event.event_id}"

        async with httpx.AsyncClient() as client:
            response = await client.patch(url, json=event.to_dict(), headers=headers)
            response.raise_for_status()
            return response.json()

    @staticmethod
    async def delete_event(event_id: str) -> dict:
        """Deletes an event from Microsoft Graph."""
        access_token = CalendarService.get_access_token()
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
        }
        url = f"{MICROSOFT_API_URL}/{event_id}"

        async with httpx.AsyncClient() as client:
            response = await client.delete(url, headers=headers)
            response.raise_for_status()
            return {'status': 'deleted', 'id': event_id}

    @staticmethod
    async def read_events(from_date: datetime, to_date: datetime) -> List[dict]:
        """Fetches calendar events within a date range."""
        access_token = CalendarService.get_access_token()
        params = {
            '$startDateTime': from_date.isoformat(),
            '$endDateTime': to_date.isoformat(),
            '$orderby': 'start/dateTime',
        }
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(MICROSOFT_API_URL, params=params, headers=headers)
            response.raise_for_status()
            return response.json().get('value', [])

    @staticmethod
    def find_available_slots(events: List[dict], required_duration: timedelta) -> List[TimeSlot]:
        """Finds available slots between existing events based on the required duration."""
        available_slots = []
        events_sorted = sorted(events, key=lambda x: x['start']['dateTime'])

        if events_sorted:
            first_event_start = datetime.fromisoformat(events_sorted[0]['start']['dateTime'])
            now = datetime.now()

            if first_event_start > now:
                gap = first_event_start - now
                if gap >= required_duration:
                    available_slots.append(TimeSlot(now, first_event_start))

            for i in range(1, len(events_sorted)):
                current_event_end = datetime.fromisoformat(events_sorted[i - 1]['end']['dateTime'])
                next_event_start = datetime.fromisoformat(events_sorted[i]['start']['dateTime'])
                gap = next_event_start - current_event_end
                if gap >= required_duration:
                    available_slots.append(TimeSlot(current_event_end, next_event_start))

            last_event_end = datetime.fromisoformat(events_sorted[-1]['end']['dateTime'])
            available_slots.append(TimeSlot(last_event_end, last_event_end + required_duration))

        return available_slots

    # ------------------------------------------------------------------
    # New tools
    # ------------------------------------------------------------------

    @staticmethod
    async def get_event(event_id: str) -> dict:
        """Fetches a single calendar event by its ID."""
        access_token = CalendarService.get_access_token()
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
        }
        url = f"{MICROSOFT_API_URL}/{event_id}"

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()

    @staticmethod
    async def list_today_events() -> List[dict]:
        """Fetches all calendar events scheduled for today."""
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = today + timedelta(days=1)
        return await CalendarService.read_events(today, end_of_day)

    @staticmethod
    async def search_events(keyword: str) -> List[dict]:
        """Searches calendar events whose subject contains the given keyword."""
        access_token = CalendarService.get_access_token()
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
            'ConsistencyLevel': 'eventual',
        }
        params = {
            '$search': f'"{keyword}"',
            '$orderby': 'start/dateTime',
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(MICROSOFT_API_URL, params=params, headers=headers)
            response.raise_for_status()
            return response.json().get('value', [])

    @staticmethod
    async def add_attendees(event_id: str, attendees: List[str]) -> dict:
        """
        Adds attendees (by email address) to an existing event.
        Merges with any existing attendees so no one is removed.
        """
        # Fetch current attendees first
        existing = await CalendarService.get_event(event_id)
        current_attendees = existing.get('attendees', [])
        current_emails = {a['emailAddress']['address'].lower() for a in current_attendees}

        # Build the merged attendee list
        new_attendees = list(current_attendees)
        for email in attendees:
            if email.lower() not in current_emails:
                new_attendees.append({
                    'emailAddress': {'address': email},
                    'type': 'required',
                })

        access_token = CalendarService.get_access_token()
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
        }
        url = f"{MICROSOFT_API_URL}/{event_id}"

        async with httpx.AsyncClient() as client:
            response = await client.patch(url, json={'attendees': new_attendees}, headers=headers)
            response.raise_for_status()
            return response.json()

    @staticmethod
    async def accept_decline_event(event_id: str, response_type: str) -> dict:
        """
        Responds to a calendar event invite.
        response_type must be 'accept', 'decline', or 'tentative'.
        """
        valid = {'accept', 'decline', 'tentative'}
        if response_type not in valid:
            raise ValueError(f"response_type must be one of {valid}, got '{response_type}'")

        endpoint_map = {
            'accept': 'accept',
            'decline': 'decline',
            'tentative': 'tentativelyAccept',
        }
        access_token = CalendarService.get_access_token()
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
        }
        url = f"https://graph.microsoft.com/v1.0/me/events/{event_id}/{endpoint_map[response_type]}"

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json={'sendResponse': True}, headers=headers)
            response.raise_for_status()
            return {'status': response_type, 'id': event_id}

