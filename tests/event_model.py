import unittest
from datetime import datetime
from models.event_model import Event


class TestEventModel(unittest.TestCase):

    def test_event_creation(self):
        # Create a new event
        event = Event('Meeting', datetime(2026, 2, 18, 9, 0), datetime(2026, 2, 18, 10, 0), 'Conference Room',
                      'organizer@example.com')

        # Assertions
        self.assertEqual(event.subject, 'Meeting')
        self.assertEqual(event.start, datetime(2026, 2, 18, 9, 0))
        self.assertEqual(event.end, datetime(2026, 2, 18, 10, 0))
        self.assertEqual(event.location, 'Conference Room')
        self.assertEqual(event.organizer, 'organizer@example.com')

    def test_to_dict(self):
        # Create a new event
        event = Event('Meeting', datetime(2026, 2, 18, 9, 0), datetime(2026, 2, 18, 10, 0), 'Conference Room',
                      'organizer@example.com')

        # Convert to dictionary
        event_dict = event.to_dict()

        # Assertions
        self.assertEqual(event_dict['subject'], 'Meeting')
        self.assertEqual(event_dict['start']['dateTime'], '2026-02-18T09:00:00')
        self.assertEqual(event_dict['location']['displayName'], 'Conference Room')


if __name__ == '__main__':
    unittest.main()
