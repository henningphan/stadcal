from icalendar import Calendar, Event
from datetime import datetime
from zoneinfo import ZoneInfo

def static_cal():
    """Used for testing"""
    tz = ZoneInfo("Europe/Stockholm")
    calendar = Calendar()

    event = Event()
    event.add("name", "name")
    event.add("description", "description")
    event.add("summary", "summary")
    event.add("dtstart", datetime(2025, 11,11, tzinfo=tz))
    event.add("dtend", datetime(2025, 11,11, tzinfo=tz))
    calendar.add_component(event)
    event = Event()
    event.add("name", "name2")
    event.add("summary", "summary2")
    event.add("description", "description2")
    event.add("dtstart", datetime(2025, 12,12, tzinfo=tz))
    event.add("dtend", datetime(2025, 12,12, tzinfo=tz))
    calendar.add_component(event)
    event = Event()
    event.add("name", "name3")
    event.add("summary", "summary3")
    event.add("description", "description3")
    event.add("dtstart", datetime(2025, 12,13, tzinfo=tz))
    event.add("dtend", datetime(2025, 12,13, tzinfo=tz))
    calendar.add_component(event)
    return calendar

def from_service_info(serviceInfos):
    calendar = Calendar()
    for si in serviceInfos:
        event = Event()
        event.add("name", "stadalliansen")
        event.add("uid", str(si.start))
        event.add("description", si.summary)
        event.add("summary", si.summary)
        event.add("dtstart", si.start)
        event.add("dtend", si.end)
        calendar.add_component(event)
    return calendar

