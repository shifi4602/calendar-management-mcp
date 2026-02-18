from datetime import datetime
from typing import Dict


class CalendarEvent:
    def __init__(self, subject: str, start: datetime, end: datetime, location: str, organizer: str):
        self.subject = subject
        self.start = start
        self.end = end
        self.location = location
        self.organizer = organizer

    @classmethod
    def from_api_data(cls, data: Dict) -> CalendarEvent:
        """ Converts API response data into CalendarEvent model. """
        return cls(
            subject=data['subject'],
            start=datetime.fromisoformat(data['start']['dateTime']),
            end=datetime.fromisoformat(data['end']['dateTime']),
            location=data.get('location', {}).get('displayName', 'No location'),
            organizer=data['organizer']['emailAddress']['address'],
        )
