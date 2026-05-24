from __future__ import annotations
from datetime import datetime, timedelta
from typing import List

from mcp.server.fastmcp import FastMCP
from models.event_model import Event
from services.calendar_service import CalendarService

mcp = FastMCP("calendar-management-mcp")


# ------------------------------------------------------------------
# Existing tools (fixed)
# ------------------------------------------------------------------

@mcp.tool(description="Retrieve calendar events from Microsoft account for a specified workweek.")
async def readWorkweekTasks(start_date: datetime) -> List[dict]:
    """Fetches calendar events for the workweek based on the start date."""
    return await CalendarService.read_events_for_workweek(start_date)


@mcp.tool(description="Create a new calendar event.")
async def createMeet(subject: str, start: datetime, end: datetime, location: str, organizer: str) -> dict:
    """Creates a new event on the calendar."""
    event = Event(subject, start, end, location, organizer)
    return await CalendarService.create_event(event)


@mcp.tool(description="Update an existing calendar event.")
async def updateMeet(event_id: str, subject: str, start: datetime, end: datetime, location: str) -> dict:
    """Updates an existing event on the calendar."""
    event = Event(subject, start, end, location, organizer="", event_id=event_id)
    return await CalendarService.update_event(event)


@mcp.tool(description="Delete a calendar event.")
async def deleteMeet(event_id: str) -> dict:
    """Deletes an event from the calendar."""
    return await CalendarService.delete_event(event_id)


@mcp.tool(description="Find available time slots in the calendar for a specified duration.")
async def findAvailableSlot(required_duration: int, start_date: datetime) -> list:
    """
    Finds available time slots for a given duration (in minutes).
    Searches the 7 days starting from start_date.
    """
    required_duration_timedelta = timedelta(minutes=required_duration)
    to_date = start_date + timedelta(days=7)
    events = await CalendarService.read_events(start_date, to_date)
    available_slots = CalendarService.find_available_slots(events, required_duration_timedelta)
    return [slot.to_dict() for slot in available_slots]


# ------------------------------------------------------------------
# New tools
# ------------------------------------------------------------------

@mcp.tool(description="Get a single calendar event by its ID.")
async def getEvent(event_id: str) -> dict:
    """Returns the full details of the event with the given ID."""
    return await CalendarService.get_event(event_id)


@mcp.tool(description="List all calendar events scheduled for today.")
async def listTodayEvents() -> List[dict]:
    """Returns all events on today's calendar in chronological order."""
    return await CalendarService.list_today_events()


@mcp.tool(description="Search calendar events by keyword in the subject.")
async def searchEvents(keyword: str) -> List[dict]:
    """Returns events whose subject contains the given keyword."""
    return await CalendarService.search_events(keyword)


@mcp.tool(description="Add one or more attendees to an existing calendar event.")
async def addAttendees(event_id: str, attendees: List[str]) -> dict:
    """
    Adds attendees to the specified event without removing existing ones.
    Provide attendees as a list of email addresses.
    """
    return await CalendarService.add_attendees(event_id, attendees)


@mcp.tool(description="Accept, decline, or tentatively accept a calendar event invite.")
async def acceptDeclineEvent(event_id: str, response: str) -> dict:
    """
    Responds to a calendar event invite.
    response must be 'accept', 'decline', or 'tentative'.
    """
    return await CalendarService.accept_decline_event(event_id, response)


if __name__ == "__main__":
    mcp.run()

