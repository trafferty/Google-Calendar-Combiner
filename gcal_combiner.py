import string
import sys
import os.path
import time
import math
import json
try:
  from xml.etree import ElementTree
except ImportError:
  from elementtree import ElementTree
import gdata.calendar.client
import gdata.calendar.data
import atom
import ImageDraw
import ImageFont
import Image

# Enums for the event object
TITLE, DATE_STR, TIME_STR, DELTA_SECS, CAL_NAME, TEXT_COLOR = range(6)
# Enums for the linesToPrint object
TEXT_TO_PRINT, FONT_COLOR = range(2)

class gcal_combiner:
   """   Google Calendar Query Combiner
      
      Allows aggregation of events from multiple google calendar accounts into a single list.

      After creation, use 'addCalendarData' to add new cal data:
        calendar_user: Google user name for calendar, ie, 'usa__en@holiday.calendar.google.com'
        visibility   : Visibility data for calendar, ie, 'public', or 'private-some_guid_data'
        cal_name     : name used to distinguish this calendar's data, ie, "JacksCal"
        font_color   : font color to be used for rendering

      Then call 'fetchCalendarEvents', which gets data from google calendar for each calendar
      which was added.  It has one argument, 'days_in_future', which limits how far in future to 
      fetch entires.
   """
      
   def __init__(self, days_in_future):
      self.calendar_client = gdata.calendar.client.CalendarClient()
      self.calendar_data = []
      self.combined_entries = []
      self.cal_entries = {}
      self.days_in_future = days_in_future

   def addCalendarData(self, calendar_user, visibility, cal_name, font_color):
      new_cal_data = []
      new_cal_data.append(calendar_user)
      new_cal_data.append(visibility)
      new_cal_data.append(cal_name)
      new_cal_data.append(font_color)
      self.calendar_data.append(new_cal_data)

   def fetchCalendarEvents(self):
      for cal_data in self.calendar_data:
         feed_uri = self.calendar_client.GetCalendarEventFeedUri(calendar=cal_data[0], visibility=cal_data[1], projection='full')
         now_ts = time.mktime(time.gmtime(time.time()))
         start_date = time.strftime("%Y-%m-%d")
         end_date = time.strftime("%Y-%m-%d", time.gmtime(time.time() + (self.days_in_future * 86400)))
         query = gdata.calendar.client.CalendarEventQuery(start_min=start_date, start_max=end_date)
         # set adjustment factor for day light savings time (5 in winter, 6 other times)
         dst_adjust = 6
         feed = self.calendar_client.GetCalendarEventFeed(uri=feed_uri, q=query)
         print "Obtained %d entries from cal: %s" % (len(feed.entry), cal_data[2])
         
         eventList = []
         for i, an_event in zip(xrange(len(feed.entry)), feed.entry):
            if (len(an_event.title.text) > 0) and (an_event.event_status.value.find('event.confirmed') >= 0):
               for a_when in an_event.when:
                  if a_when.start.find('T') > 0:
                     print "Event %d: %s" % (i, a_when)
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
                  print '\t%s: %s (delta_secs: %d)' % (an_event.title.text, eventDateTimeStr, delta_secs)
                  
                  '''build the event:
                     [event_title, event_date, event_time, event_delta_secs]
                     ...then add to the event list
                  '''
                  event = []
                  event.append(cal_data[2])          # add cal_name
                  event.append(delta_secs)           # add DELTA_SECS
                  event.append(an_event.title.text)  # add TITLE
                  event.append(eventDate)      # add DATE_STR
                  event.append(eventTime)      # add TIME_STR
                  # append to the event list
                  eventList.append(event)

         new_combined_entry = []
         new_combined_entry.append(eventList)
         new_combined_entry.append(cal_data[2])
         new_combined_entry.append(cal_data[3])
         self.combined_entries.append(new_combined_entry)

      self.total_entries = 0
      print '*********************************************************'
      print "Fetched data from %d calendars:" % len(self.combined_entries)
      for combined_entry in self.combined_entries:
         self.total_entries += len(combined_entry[0])
         print "\t%s: %d events" % (combined_entry[1], len(combined_entry[0]))
      print "Total entries in next %d days: %d" % ( self.days_in_future, self.total_entries)

   def buildEventList(self):
      # sort it based on delta (earliest first)
      eventList_sorted = sorted(self.combined_entries, key=lambda days: days[2])
      
      # next, build the list of lines to print.
      self.linesToPrint_list = []
      # for each event, build a line string, then add line plus font color to line
      # to print object, then add this to list of lines to print
      for event in eventList_sorted:
         print " event:"
         print event
         # # we only want events that are in the future, but no more than 90 days
         # if (event[DELTA_SECS] > -1) and (event[DELTA_SECS] <= (self.days_in_future*86400)):
         #    # if delta_secs is less than a day, print in hours
         #    if event[DELTA_SECS] > 86400:
         #       delta_days = round(event[DELTA_SECS]/86400.0)
         #       line = "%02dd: %s, %s (%s)" % (delta_days, event[TITLE], event[DATE_STR], event[TIME_STR])
         #    else:
         #       delta_hours = round(event[DELTA_SECS]/3600.0)
         #       line = "%02dh: %s, %s (%s)" % (delta_hours, event[TITLE], event[DATE_STR], event[TIME_STR])            
         #    lineToPrint = []
         #    lineToPrint.append(line)               # add TEXT_TO_PRINT
         #    lineToPrint.append(event[TEXT_COLOR])  # add FONT_COLOR
         #    self.linesToPrint_list.append(lineToPrint)
         #    print "Added (%s) - %s" % (event[CAL_NAME], line)
         # else:
         #    line = "%02dd: %s, %s (%s)" % (event[DELTA_SECS], event[TITLE], event[DATE_STR], event[TIME_STR])
         #    print "Omitted (%s) - %s" % (event[CAL_NAME], line)


