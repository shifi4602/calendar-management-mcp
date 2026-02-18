# models.py
from datetime import datetime, timedelta

class TimeSlot:
    def __init__(self, start: datetime, end: datetime):
        self.start = start
        self.end = end

    def duration(self) -> timedelta:
        """ Returns the duration of the time slot. """
        return self.end - self.start

    def to_dict(self) -> dict:
        """ Convert the TimeSlot to a dictionary. """
        return {
            'start': self.start.isoformat(),
            'end': self.end.isoformat(),
            'duration': str(self.duration())
        }
