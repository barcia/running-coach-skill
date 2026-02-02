---
name: ical
description: Create .ics calendar files for importing events into Apple Calendar, Google Calendar, Outlook, etc. Use when asked to "create calendar event", "add to calendar", "export to ics", "generate ical", or when creating scheduled events that need calendar import.
---

# ICAL Event Creator

Generate `.ics` files

## File Structure

```
BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Claude//EN
CALSCALE:GREGORIAN
METHOD:PUBLISH
BEGIN:VEVENT
UID:unique-id@domain
DTSTAMP:20260120T100000Z
DTSTART:20260121T180000
DTEND:20260121T190000
SUMMARY:Event Title
DESCRIPTION:Event details here
STATUS:TENTATIVE
END:VEVENT
END:VCALENDAR
```

## Required Fields

**VCALENDAR:** `VERSION:2.0`, `PRODID`, `CALSCALE:GREGORIAN`, `METHOD:PUBLISH`

**VEVENT:** `UID` (unique), `DTSTAMP` (UTC with Z), `DTSTART`, `DTEND`, `SUMMARY`

## Date Formats

- Local: `YYYYMMDDTHHMMSS` → `20260121T180000`
- UTC: `YYYYMMDDTHHMMSSZ` → `20260121T170000Z`
- All-day: `YYYYMMDD` → `20260121`

## Escaping in DESCRIPTION

Use `\n` for newlines, `\,` for commas, `\;` for semicolons.

## Optional Fields

- `DESCRIPTION` - Event details
- `LOCATION` - Place
- `CATEGORIES` - Tags (comma-separated)
- `STATUS:TENTATIVE` - Marks as proposed

## Filename

`event_YYYY-MM-DD.ics` or descriptive name like `meeting_project.ics`
