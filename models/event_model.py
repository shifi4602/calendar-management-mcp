from datetime import datetime


class Event:
    def __init__(self, subject: str, start: datetime, end: datetime, location: str, organizer: str,
                 event_id: str = None):
        self.subject = subject
        self.start = start
        self.end = end
        self.location = location
        self.organizer = organizer
        self.event_id = event_id  # Optional, only needed for update/delete

    def to_dict(self) -> dict:
        """ Converts the Event object to a dictionary format for API consumption. """
        return {
            'subject': self.subject,
            'start': {'dateTime': self.start.isoformat(), 'timeZone': 'UTC'},
            'end': {'dateTime': self.end.isoformat(), 'timeZone': 'UTC'},
            'location': {'displayName': self.location},
            'organizer': {'emailAddress': {'address': self.organizer}},
        }
