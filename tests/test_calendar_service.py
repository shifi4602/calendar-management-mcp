import unittest
from unittest.mock import patch, AsyncMock, MagicMock
from datetime import datetime, timedelta

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from services.calendar_service import CalendarService
from models.time_slot_model import TimeSlot


class TestGetWorkweekDates(unittest.IsolatedAsyncioTestCase):

    async def test_monday_start(self):
        # Wednesday 2026-02-18 → week should start Monday 2026-02-16
        start, end = await CalendarService.get_workweek_dates(datetime(2026, 2, 18))
        self.assertEqual(start.weekday(), 0)   # Monday
        self.assertEqual(end.weekday(), 4)     # Friday

    async def test_monday_input(self):
        start, end = await CalendarService.get_workweek_dates(datetime(2026, 2, 16))
        self.assertEqual(start, datetime(2026, 2, 16))
        self.assertEqual(end, datetime(2026, 2, 20))

    async def test_five_day_span(self):
        start, end = await CalendarService.get_workweek_dates(datetime(2026, 5, 20))
        self.assertEqual((end - start).days, 4)


class TestFindAvailableSlots(unittest.TestCase):

    def _make_event(self, start_iso: str, end_iso: str) -> dict:
        return {
            'subject': 'Event',
            'start': {'dateTime': start_iso},
            'end': {'dateTime': end_iso},
        }

    def test_gap_between_events_is_found(self):
        events = [
            self._make_event('2026-02-18T09:00:00', '2026-02-18T10:00:00'),
            self._make_event('2026-02-18T12:00:00', '2026-02-18T13:00:00'),
        ]
        slots = CalendarService.find_available_slots(events, timedelta(minutes=30))
        # The gap 10:00–12:00 is 2 hours → should be included
        slot_starts = [s.start.hour for s in slots]
        self.assertIn(10, slot_starts)

    def test_small_gap_is_excluded(self):
        events = [
            self._make_event('2026-02-18T09:00:00', '2026-02-18T10:00:00'),
            self._make_event('2026-02-18T10:15:00', '2026-02-18T11:00:00'),
        ]
        # Gap is only 15 minutes; require 30 → should not be returned
        slots = CalendarService.find_available_slots(events, timedelta(minutes=30))
        gap_10_to_10_15 = [s for s in slots if s.start.hour == 10 and s.end.hour == 10 and s.end.minute == 15]
        self.assertEqual(len(gap_10_to_10_15), 0)

    def test_empty_events_returns_no_slots(self):
        slots = CalendarService.find_available_slots([], timedelta(minutes=30))
        self.assertEqual(slots, [])

    def test_slot_after_last_event_appended(self):
        events = [
            self._make_event('2026-02-18T09:00:00', '2026-02-18T10:00:00'),
        ]
        slots = CalendarService.find_available_slots(events, timedelta(minutes=60))
        # Last slot starts at end of last event
        last = slots[-1]
        self.assertEqual(last.start, datetime(2026, 2, 18, 10, 0))
        self.assertEqual(last.end, datetime(2026, 2, 18, 11, 0))


class TestCalendarServiceHTTP(unittest.IsolatedAsyncioTestCase):
    """Tests for methods that call Microsoft Graph, with HTTP mocked."""

    def _auth_patch(self):
        return patch('services.calendar_service.CalendarService.get_access_token', return_value='fake_token')

    @patch('httpx.AsyncClient')
    async def test_create_event(self, mock_client_cls):
        mock_response = MagicMock()
        mock_response.json.return_value = {'id': 'new_id', 'subject': 'Test'}
        mock_response.raise_for_status = MagicMock()
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client_cls.return_value = mock_client

        with self._auth_patch():
            from models.event_model import Event
            event = Event('Test', datetime(2026, 2, 18, 9), datetime(2026, 2, 18, 10), 'Room A', 'org@test.com')
            result = await CalendarService.create_event(event)

        self.assertEqual(result['subject'], 'Test')

    @patch('httpx.AsyncClient')
    async def test_delete_event(self, mock_client_cls):
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.delete = AsyncMock(return_value=mock_response)
        mock_client_cls.return_value = mock_client

        with self._auth_patch():
            result = await CalendarService.delete_event('event_id_123')

        self.assertEqual(result['status'], 'deleted')
        self.assertEqual(result['id'], 'event_id_123')

    @patch('httpx.AsyncClient')
    async def test_search_events(self, mock_client_cls):
        mock_response = MagicMock()
        mock_response.json.return_value = {'value': [{'subject': 'Sprint Planning'}]}
        mock_response.raise_for_status = MagicMock()
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client_cls.return_value = mock_client

        with self._auth_patch():
            result = await CalendarService.search_events('Sprint')

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['subject'], 'Sprint Planning')

    async def test_accept_decline_invalid_raises(self):
        with self.assertRaises(ValueError):
            await CalendarService.accept_decline_event('id', 'maybe')

    @patch('httpx.AsyncClient')
    async def test_accept_event(self, mock_client_cls):
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client_cls.return_value = mock_client

        with self._auth_patch():
            result = await CalendarService.accept_decline_event('event_id_123', 'accept')

        self.assertEqual(result['status'], 'accept')


if __name__ == '__main__':
    unittest.main()
