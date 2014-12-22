import string
import sys
import os.path
import time
import datetime
import math
# try:
#   from xml.etree import ElementTree
# except ImportError:
#   from elementtree import ElementTree
# import gdata.calendar.client
# import gdata.calendar.data
# import atom
import GoogleAPIHelper as gAPI

# Enums for the event object:
# ['cal_name', delta_sec, 'event_title', 'event_date', 'event_time']
CAL_NAME, DELTA_SECS, TITLE, DATE_STR, TIME_STR = range(5)

class gcal_combiner:
    """   Google Calendar Query Combiner
           
           Allows aggregation of events from multiple google calendar accounts into a single list.

           Create an instance of the gcal_combiner class, passing in the number of days in the future that 
           you want to get calendar data from.

           After instantiation, use 'addCalendarData' to add new calender data:
               calendar_user: Google user name for calendar, ie, 'usa__en@holiday.calendar.google.com'
               visibility   : Visibility data for calendar, ie, 'public', or 'private-some_guid_data'
               cal_name     : name used to distinguish this calendar's data, ie, "JacksCal"

           Then call 'fetchCalendarEvents', which uses gdata.calendar.client to get data from google 
           calendar for each calendar which was added.  This method produces a single list of events
           from all calendars.

           Finally, a call to 'buildLinesToPrint' takes the combined list of events, sorts it according 
           to events closest in the future, and formats the lines into a list that is returned.
    """
           
    def __init__(self):
        #
        # Some member vars
        self.calendar_data = []
        self.combined_events = []

    def addCalendarData(self, cal_id, cal_name):
        self.calendar_data.append({'cal_id': cal_id, 'cal_name': cal_name})

    def fetchCalendarEvents(self, num_days_to_search, discovery_file_path):
        # get a handle to an API service 
        scope='https://www.googleapis.com/auth/calendar.readonly'
        service, flags = gAPI.getAPIservice(
            [], 'calendar', 'v3', discovery_file_path, scope)

        # set adjustment factor for dst
        if time.localtime().tm_isdst == 0:
             dst_adjust = 6
        else:
             dst_adjust = 5

        # set the min and max times for event fetch
        now_ts = datetime.datetime.today()
        time_min = now_ts.isoformat()[0:-4]
        future_ts = now_ts + datetime.timedelta(days=num_days_to_search)
        time_max = future_ts.isoformat()[0:-4]

        page_token = None
        for cal_data in self.calendar_data:
             print(">>>>>>>>>> Events for calendar id: %s" % cal_data['cal_name'])
             while True:
                events = service.events().list(calendarId=cal_data['cal_id'], timeMax=time_max, timeMin=time_min, pageToken=page_token).execute()
                for event in events['items']:
                    if 'summary' in event:
                        if 'dateTime' in event['start']:
                            event['all_day'] = False
                            event_start, event_time = event['start']['dateTime'].split('T')

                            # convert date from "YYYY-MM-DD" to "Day, Mon date"
                            eventDate = time.strftime("%a, %b %d", time.strptime(event_start, "%Y-%m-%d"))

                            # parse out HH, MM and convert time from 24hr to 12hr format
                            hour, min = event_time[0:5].split(':')
                            if int(hour) > 12:
                                eventTime = '%d:%sP' % ((int(hour) - 12), min)
                            elif int(hour) == 12:
                                eventTime = eventTime + 'P'
                            else:
                                eventTime = eventTime + 'A'

                            eventDateTimeStr = "%s - %s" % (eventDate, eventTime)
                            event_ts = time.mktime(time.strptime(event['start']['dateTime'][0:19], "%Y-%m-%dT%H:%M:%S")) + (dst_adjust * 3600)
                        else:
                            event['all_day'] = True
                            event_start = event['start']['date']
                            eventTime = "All Day"

                            # convert date from "YYYY-MM-DD" to "Day, Mon date"
                            eventDate = time.strftime("%a, %b %d", time.strptime(event_start[0:10], "%Y-%m-%d"))
                            eventDateTimeStr = "%s" % (eventDate)
                            event_ts = time.mktime(time.strptime(event_start[0:19], "%Y-%m-%d")) + (dst_adjust * 3600)

                        delta_secs = int(event_ts - now_ts)
                        #print '\t%s: %s (delta_secs: %d)' % (an_event.title.text, eventDateTimeStr, delta_secs)
                        
                        '''
                             build the new event:
                             [cal_name, event_delta_secs, event_title, event_date, event_time]
                             ...then add to the combined event list
                        '''
                        new_event = []
                        new_event.append(cal_data['cal_name']) # add cal_name
                        new_event.append(delta_secs)           # add DELTA_SECS
                        new_event.append(event['summary'])     # add TITLE
                        new_event.append(eventDate)            # add DATE_STR
                        new_event.append(eventTime)            # add TIME_STR
                        # append to the event list
                        self.combined_events.append(new_event)

                page_token = events.get('nextPageToken')
                if not page_token:
                    break
        self.total_entries = 0
        print '*********************************************************'
        print "Fetched data from %d calendars:" % len(self.calendar_data)

    def buildLinesToPrint(self):
        # sort it based on delta (earliest first)
        eventList_sorted = sorted(self.combined_events, key=lambda days: days[1])
        
        linesToPrint = []
        # next, build the list of lines to print.
        # for each event, build a line string, then add line plus cal_name to list
        # of lines to print
        for event in eventList_sorted:
            if (event[DELTA_SECS] > -1) and (event[DELTA_SECS] <= (self.days_in_future*86400)):
                # if delta_secs is less than 2 hours, print in min
                # if delta_secs is less than a day, print in hours
                if event[DELTA_SECS] > 86400:
                    delta_days = round(event[DELTA_SECS]/86400.0)
                    line = "%02dd: %s, %s (%s)" % (delta_days, event[TITLE], event[DATE_STR], event[TIME_STR])
                else:
                    delta_hours = round(event[DELTA_SECS]/3600.0)
                    line = "%02dh: %s, %s (%s)" % (delta_hours, event[TITLE], event[DATE_STR], event[TIME_STR])            
                lineToPrint = []
                lineToPrint.append(line)             # add text 
                lineToPrint.append(event[CAL_NAME])  # add CAL_NAME
                linesToPrint.append(lineToPrint)
                print "Added (%s) - %s" % (lineToPrint[1], lineToPrint[0])
            else:
                line = "%02dd: %s, %s (%s)" % (event[DELTA_SECS], event[TITLE], event[DATE_STR], event[TIME_STR])
                print "Omitted (%s) - %s" % (event[CAL_NAME], line)
        return linesToPrint


