import datetime
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import os
import sys
from dotenv import load_dotenv
from dateutil.parser import parse

# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'


def datetime_from_google_dict(dt_dict):
    if 'dateTime' in dt_dict:
        dt = parse(dt_dict['dateTime'])
    if 'date' in dt_dict:
        dt = parse(dt_dict['date'])
        dt = dt.replace(tzinfo=datetime.timezone.utc)
    return dt


def main():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('calendar', 'v3', http=creds.authorize(Http()))

    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    print('Getting the upcoming 10 events')

    # must be in ['x','y','z'] format
    calendar_ids = eval(os.getenv("CALENDAR_IDS"))

    events = list()
    for calendar_id in calendar_ids:
        events_result = service.events().list(calendarId=calendar_id, timeMin=now,
                                              maxResults=10, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events + events_result.get('items', [])

    events.sort(key=lambda k: datetime_from_google_dict(k['start']))

    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary'])


if __name__ == '__main__':
    # run in own directory
    os.chdir(os.path.dirname(sys.argv[0]))
    load_dotenv()
    main()

