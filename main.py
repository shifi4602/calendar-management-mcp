from __future__ import annotations
import asyncio
from datetime import datetime, timedelta
from typing import List

from mcp.server.fastmcp import FastMCP
from models.event_model import Event
from services.calendar_service import CalendarService

mcp = FastMCP("calendar-management-mcp")


@mcp.tool(description="Retrieve calendar events from Microsoft account for a specified workweek.")
async def readWorkweekTasks(start_date: datetime) -> List[dict]:
    """ Fetches calendar events for the workweek based on the start date. """
    events = await CalendarService.read_events_for_workweek(start_date)
    return events


@mcp.tool(description="Create a new calendar event.")
async def createMeet(subject: str, start: datetime, end: datetime, location: str, organizer: str) -> dict:
    """ Creates a new event on the calendar. """
    event = Event(subject, start, end, location, organizer)
    new_event = await CalendarService.create_event(event)
    return new_event


@mcp.tool(description="Update an existing calendar event.")
async def updateMeet(event_id: str, subject: str, start: datetime, end: datetime, location: str) -> dict:
    """ Updates an existing event on the calendar. """
    event = Event(subject, start, end, location, organizer="")  # Assuming the organizer is updated elsewhere
    event.event_id = event_id
    updated_event = await CalendarService.update_event(event)
    return updated_event


@mcp.tool(description="Delete a calendar event.")
async def deleteMeet(event_id: str) -> dict:
    """ Deletes an event from the calendar. """
    result = await CalendarService.delete_event(event_id)
    return result

@mcp.tool(description="Find available time slots in the calendar for a specified duration.")
async def findAvailableSlot(required_duration: int, start_date: datetime) -> list:
    """ Finds available time slots for a given duration (in minutes) from the calendar. """
    # Convert the required duration to a timedelta
    required_duration_timedelta = timedelta(minutes=required_duration)

    # Fetch events for the given date range (e.g., workweek or today)
    to_date = start_date + timedelta(days=7)  # Let's check for the next 7 days
    events = await CalendarService.read_events(start_date, to_date)

    # Find available slots
    available_slots = CalendarService.find_available_slots(events, required_duration_timedelta)

    # Convert available slots to dictionary format for easy response
    available_slots_dict = [slot.to_dict() for slot in available_slots]

    return available_slots_dict


# Example usage: Read tasks from a specific workweek
# if __name__ == "__main__":
#     start_date = datetime.now()
#
#     loop = asyncio.get_event_loop()
#     events = loop.run_until_complete(readWorkweekTasks(start_date))
#     print(events)
