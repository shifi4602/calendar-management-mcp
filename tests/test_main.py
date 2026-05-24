import unittest
from unittest.mock import patch, AsyncMock, MagicMock
from datetime import datetime, timedelta

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from main import (
    readWorkweekTasks,
    createMeet,
    updateMeet,
    deleteMeet,
    findAvailableSlot,
    getEvent,
    listTodayEvents,
    searchEvents,
    addAttendees,
    acceptDeclineEvent,
)
from models.time_slot_model import TimeSlot


class TestReadWorkweekTasks(unittest.IsolatedAsyncioTestCase):

    @patch('services.calendar_service.CalendarService.read_events_for_workweek', new_callable=AsyncMock)
    async def test_returns_events(self, mock_read):
        mock_read.return_value = [{'subject': 'Meeting with HR'}]
        events = await readWorkweekTasks(datetime(2026, 2, 18))
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]['subject'], 'Meeting with HR')
        mock_read.assert_awaited_once()


class TestCreateMeet(unittest.IsolatedAsyncioTestCase):

    @patch('services.calendar_service.CalendarService.create_event', new_callable=AsyncMock)
    async def test_creates_event(self, mock_create):
        mock_create.return_value = {'subject': 'New Event', 'id': 'abc123'}
        result = await createMeet(
            'New Event',
            datetime(2026, 2, 18, 9, 0),
            datetime(2026, 2, 18, 10, 0),
            'Conference Room',
            'organizer@example.com',
        )
        self.assertEqual(result['subject'], 'New Event')
        mock_create.assert_awaited_once()


class TestUpdateMeet(unittest.IsolatedAsyncioTestCase):

    @patch('services.calendar_service.CalendarService.update_event', new_callable=AsyncMock)
    async def test_updates_event(self, mock_update):
        mock_update.return_value = {'subject': 'Updated Event', 'id': 'abc123'}
        result = await updateMeet(
            'abc123',
            'Updated Event',
            datetime(2026, 2, 18, 9, 0),
            datetime(2026, 2, 18, 11, 0),
            'Room B',
        )
        self.assertEqual(result['subject'], 'Updated Event')
        mock_update.assert_awaited_once()


class TestDeleteMeet(unittest.IsolatedAsyncioTestCase):

    @patch('services.calendar_service.CalendarService.delete_event', new_callable=AsyncMock)
    async def test_deletes_event(self, mock_delete):
        mock_delete.return_value = {'status': 'deleted', 'id': 'abc123'}
        result = await deleteMeet('abc123')
        self.assertEqual(result['status'], 'deleted')
        mock_delete.assert_awaited_once_with('abc123')


class TestFindAvailableSlot(unittest.IsolatedAsyncioTestCase):

    @patch('services.calendar_service.CalendarService.read_events', new_callable=AsyncMock)
    async def test_finds_slots(self, mock_read):
        mock_read.return_value = [
            {
                'subject': 'Morning Standup',
                'start': {'dateTime': '2026-02-18T09:00:00'},
                'end': {'dateTime': '2026-02-18T10:00:00'},
            },
            {
                'subject': 'Lunch Meeting',
                'start': {'dateTime': '2026-02-18T12:00:00'},
                'end': {'dateTime': '2026-02-18T13:00:00'},
            },
        ]
        slots = await findAvailableSlot(30, datetime(2026, 2, 18, 8, 0))
        self.assertIsInstance(slots, list)
        # At least one slot should exist between events
        self.assertGreater(len(slots), 0)
        # Each slot should have start, end, duration
        self.assertIn('start', slots[0])
        self.assertIn('end', slots[0])


# ------------------------------------------------------------------
# New tools
# ------------------------------------------------------------------

class TestGetEvent(unittest.IsolatedAsyncioTestCase):

    @patch('services.calendar_service.CalendarService.get_event', new_callable=AsyncMock)
    async def test_gets_event(self, mock_get):
        mock_get.return_value = {'id': 'abc123', 'subject': 'Team Sync'}
        result = await getEvent('abc123')
        self.assertEqual(result['id'], 'abc123')
        self.assertEqual(result['subject'], 'Team Sync')
        mock_get.assert_awaited_once_with('abc123')


class TestListTodayEvents(unittest.IsolatedAsyncioTestCase):

    @patch('services.calendar_service.CalendarService.list_today_events', new_callable=AsyncMock)
    async def test_lists_today(self, mock_list):
        mock_list.return_value = [{'subject': 'Daily Standup'}, {'subject': 'Code Review'}]
        result = await listTodayEvents()
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['subject'], 'Daily Standup')


class TestSearchEvents(unittest.IsolatedAsyncioTestCase):

    @patch('services.calendar_service.CalendarService.search_events', new_callable=AsyncMock)
    async def test_searches_events(self, mock_search):
        mock_search.return_value = [{'subject': 'Sprint Planning'}]
        result = await searchEvents('Sprint')
        self.assertEqual(len(result), 1)
        mock_search.assert_awaited_once_with('Sprint')


class TestAddAttendees(unittest.IsolatedAsyncioTestCase):

    @patch('services.calendar_service.CalendarService.add_attendees', new_callable=AsyncMock)
    async def test_adds_attendees(self, mock_add):
        mock_add.return_value = {'id': 'abc123', 'subject': 'Planning'}
        result = await addAttendees('abc123', ['alice@example.com', 'bob@example.com'])
        self.assertEqual(result['id'], 'abc123')
        mock_add.assert_awaited_once_with('abc123', ['alice@example.com', 'bob@example.com'])


class TestAcceptDeclineEvent(unittest.IsolatedAsyncioTestCase):

    @patch('services.calendar_service.CalendarService.accept_decline_event', new_callable=AsyncMock)
    async def test_accepts_event(self, mock_respond):
        mock_respond.return_value = {'status': 'accept', 'id': 'abc123'}
        result = await acceptDeclineEvent('abc123', 'accept')
        self.assertEqual(result['status'], 'accept')
        mock_respond.assert_awaited_once_with('abc123', 'accept')

    @patch('services.calendar_service.CalendarService.accept_decline_event', new_callable=AsyncMock)
    async def test_declines_event(self, mock_respond):
        mock_respond.return_value = {'status': 'decline', 'id': 'abc123'}
        result = await acceptDeclineEvent('abc123', 'decline')
        self.assertEqual(result['status'], 'decline')


if __name__ == '__main__':
    unittest.main()


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

