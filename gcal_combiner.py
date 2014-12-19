import string
import sys
import os.path
import time
import math
try:
  from xml.etree import ElementTree
except ImportError:
  from elementtree import ElementTree
import gdata.calendar.client
import gdata.calendar.data
import atom

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
      
   def __init__(self, days_in_future):
      self.calendar_client = gdata.calendar.client.CalendarClient()
      self.calendar_data = []
      self.combined_events = []
      self.days_in_future = days_in_future

   def addCalendarData(self, calendar_user, visibility, cal_name):
      new_cal_data = []
      new_cal_data.append(calendar_user)
      new_cal_data.append(visibility)
      new_cal_data.append(cal_name)
      self.calendar_data.append(new_cal_data)

   def fetchCalendarEvents(self):
      for cal_data in self.calendar_data:
         feed_uri = self.calendar_client.GetCalendarEventFeedUri(calendar=cal_data[0], visibility=cal_data[1], projection='full')
         now_ts = time.mktime(time.gmtime(time.time()))
         start_date = time.strftime("%Y-%m-%d")
         end_date = time.strftime("%Y-%m-%d", time.gmtime(time.time() + (self.days_in_future * 86400)))
         query = gdata.calendar.client.CalendarEventQuery(start_min=start_date, start_max=end_date)
         # set adjustment factor for day light savings time (5 in winter, 6 other times)
         if time.localtime().tm_isdst == 0:
            dst_adjust = 6
         else:
            dst_adjust = 5
         feed = self.calendar_client.GetCalendarEventFeed(uri=feed_uri, q=query)
         print "Obtained %d entries from cal: %s" % (len(feed.entry), cal_data[2])
         
         eventList = []
         for i, an_event in zip(xrange(len(feed.entry)), feed.entry):
            if (len(an_event.title.text) > 0) and (an_event.event_status.value.find('event.confirmed') >= 0):
               for a_when in an_event.when:
                  if a_when.start.find('T') > 0:
                     #print "Event %d: %s" % (i, a_when)
                     event_start = a_when.start[0:19]
                     event_end = a_when.end[0:10]
                     eventDate, eventTime = a_when.start.split('T')
                     # convert date from "YYYY-MM-DD" to "Day, Mon date", and truncate time to HH:MM
                     eventDate = time.strftime("%a, %b %d", time.strptime(eventDate, "%Y-%m-%d"))
                     eventTime = eventTime[0:5]
                     # convert time from 24hr to 12hr format
                     hour, min = eventTime.split(':')
                     if int(hour) > 12:
                        eventTime = '%d:%sP' % ((int(hour) - 12), min)
                     elif int(hour) == 12:
                         eventTime = eventTime + 'P'
                     else:
                         eventTime = eventTime + 'A'
                     eventDateTimeStr = "%s - %s" % (eventDate, eventTime)
                     event_ts = time.mktime(time.strptime(event_start, "%Y-%m-%dT%H:%M:%S")) + (dst_adjust * 3600)
                  else:
                     event_start = a_when.start[0:10]
                     event_end = a_when.end[0:10]
                     eventDate = time.strftime("%a, %b %d", time.strptime(event_start[0:10], "%Y-%m-%d"))
                     eventTime = "All Day"
                     eventDateTimeStr = "%s" % (eventDate)
                     event_ts = time.mktime(time.strptime(event_start, "%Y-%m-%d")) + (dst_adjust * 3600)

                  delta_secs = int(event_ts - now_ts)
                  #print '\t%s: %s (delta_secs: %d)' % (an_event.title.text, eventDateTimeStr, delta_secs)
                  
                  '''build the event:
                     [cal_name, event_delta_secs, event_title, event_date, event_time]
                     ...then add to the combined event list
                  '''
                  event = []
                  event.append(cal_data[2])          # add cal_name
                  event.append(delta_secs)           # add DELTA_SECS
                  event.append(an_event.title.text)  # add TITLE
                  event.append(eventDate)            # add DATE_STR
                  event.append(eventTime)            # add TIME_STR
                  # append to the event list
                  self.combined_events.append(event)

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


