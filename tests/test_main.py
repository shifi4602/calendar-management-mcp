import unittest
from unittest.mock import patch, AsyncMock
from datetime import datetime, timedelta
from main import readWorkweekTasks, createMeet, updateMeet, deleteMeet
from event_model import Event
from services.calendar_service import CalendarService
from models.time_slot_model import TimeSlot


import unittest
from unittest.mock import patch, AsyncMock
from datetime import datetime, timedelta
from main import findAvailableSlot


class TestMainFunctions(unittest.TestCase):

    @patch('calendar_service.CalendarService.read_events_for_workweek')  # Mock the service method
    async def test_read_workweek_tasks(self, mock_read_events):
        # Simulate the return value
        mock_read_events.return_value = [{'subject': 'Meeting with HR'}]

        # Test the function
        start_date = datetime(2026, 2, 18)
        events = await readWorkweekTasks(start_date)

        # Assertions
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]['subject'], 'Meeting with HR')

    @patch('calendar_service.CalendarService.create_event')  # Mock the service method
    async def test_create_meet(self, mock_create_event):
        # Simulate the return value
        mock_create_event.return_value = {'subject': 'New Event'}

        # Test the function
        event = Event('New Event', datetime(2026, 2, 18, 9, 0), datetime(2026, 2, 18, 10, 0), 'Conference Room',
                      'organizer@example.com')
        result = await createMeet('New Event', datetime(2026, 2, 18, 9, 0), datetime(2026, 2, 18, 10, 0),
                                  'Conference Room', 'organizer@example.com')

        # Assertions
        self.assertEqual(result['subject'], 'New Event')

    @patch('calendar_service.CalendarService.update_event')  # Mock the service method
    async def test_update_meet(self, mock_update_event):
        # Simulate the return value
        mock_update_event.return_value = {'subject': 'New Event'}

    @patch('calendar_service.CalendarService.read_events')  # Mock the read_events method
    @patch('calendar_service.CalendarService.find_available_slots')  # Mock the find_available_slots method
    async def test_find_available_slot(self, mock_find_available_slots, mock_read_events):
        # Define the required duration for the free time slot (e.g., 30 minutes)
        required_duration = 30  # minutes
        required_duration_timedelta = timedelta(minutes=required_duration)

        # Mock the events returned by the read_events method
        mock_events = [
            {
                'subject': 'Meeting with HR',
                'start': {'dateTime': '2026-02-18T09:00:00'},
                'end': {'dateTime': '2026-02-18T10:00:00'},
                'location': {'displayName': 'Conference Room 1'},
                'organizer': {'emailAddress': {'address': 'hr@example.com'}}
            },
            {
                'subject': 'Project Discussion',
                'start': {'dateTime': '2026-02-18T11:00:00'},
                'end': {'dateTime': '2026-02-18T12:00:00'},
                'location': {'displayName': 'Conference Room 2'},
                'organizer': {'emailAddress': {'address': 'manager@example.com'}}
            }
        ]
        mock_read_events.return_value = mock_events  # Mock the event data

        # Mock the available slots
        mock_available_slots = [
            TimeSlot(datetime(2026, 2, 18, 10, 0), datetime(2026, 2, 18, 10, 30)),
            TimeSlot(datetime(2026, 2, 18, 12, 0), datetime(2026, 2, 18, 12, 30)),
        ]
        mock_find_available_slots.return_value = mock_available_slots  # Mock the available slots

        # Test the function
        start_date = datetime(2026, 2, 18, 0, 0)  # Starting from the beginning of the day
        available_slots = await findAvailableSlot(required_duration, start_date)

        # Assertions
        self.assertEqual(len(available_slots), 2)  # Should return two available slots
        self.assertEqual(available_slots[0]['start'], '2026-02-18T10:00:00')
        self.assertEqual(available_slots[1]['start'], '2026-02-18T12:00:00')
        self.assertEqual(available_slots[0]['duration'], '0:30:00')  # The duration should be 30 minutes

    @patch('calendar_service.CalendarService.read_events')  # Mock the read_events method
    async def test_no_available_slots(self, mock_read_events):
        # Define the required duration for the free time slot (e.g., 1 hour)
        required_duration = 60  # minutes
        required_duration_timedelta = timedelta(minutes=required_duration)

        # Mock the events returned by the read_events method
        mock_events = [
            {
                'subject': 'Meeting with HR',
                'start': {'dateTime': '2026-02-18T09:00:00'},
                'end': {'dateTime': '2026-02-18T10:00:00'},
                'location': {'displayName': 'Conference Room 1'},
                'organizer': {'emailAddress': {'address': 'hr@example.com'}}
            },
            {
                'subject': 'Project Discussion',
                'start': {'dateTime': '2026-02-18T11:00:00'},
                'end': {'dateTime': '2026-02-18T12:00:00'},
                'location': {'displayName': 'Conference Room 2'},
                'organizer': {'emailAddress': {'address': 'manager@example.com'}}
            }
        ]
        mock_read_events.return_value = mock_events  # Mock the event data

        # Test the function when no slots are available
        start_date = datetime(2026, 2, 18, 0, 0)  # Starting from the beginning of the day
        available_slots = await findAvailableSlot(required_duration, start_date)

        # Assertions
        self.assertEqual(len(available_slots), 0)  # No available slots of 1 hour

