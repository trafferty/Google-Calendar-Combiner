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

def GetEntriesFromFeed(cal_URIParms, daysInFuture):
   '''
    cal_URIParms = [google ID, magic cookie]
   '''
   calendar_client = gdata.calendar.client.CalendarClient()
   username = cal_URIParms[0]
   visibility = cal_URIParms[1]
   projection = 'full'
   feed_uri = calendar_client.GetCalendarEventFeedUri(calendar=username, visibility=visibility, projection=projection)
   now_ts = time.mktime(time.gmtime(time.time()))
   start_date = time.strftime("%Y-%m-%d")
   end_date = time.strftime("%Y-%m-%d", time.gmtime(time.time() + (daysInFuture * 86400)))
   query = gdata.calendar.client.CalendarEventQuery(start_min=start_date, start_max=end_date)
   # set adjustment factor for day light savings time (5 in winter, 6 other times)
   dst_adjust = 6
   feed = calendar_client.GetCalendarEventFeed(uri=feed_uri, q=query)
   print "Obtained %d entries from cal: %s" % (len(feed.entry), username)
   
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
            
            # build the event...
            event = []
            event.append(an_event.title.text)  # add TITLE
            event.append(eventDate)      # add DATE_STR
            event.append(eventTime)      # add TIME_STR
            event.append(delta_secs)        # add DELTA_SECS
            # append to the event list
            eventList.append(event)
   return eventList

def AddEntriesToEventList(entries, calName, textColor, eventList):
   for event in entries:
      event.append(calName)      # add CAL_NAME
      event.append(textColor)    # add TEXT_COLOR
      # append to the event list
      eventList.append(event)

def main(path_to_config_json_file):
   config = json.load(open(path_to_config_json_file[0]))
   #print config
      
   # initialize the eventList
   eventList = []
   
   # for each cal, use the gdata calendar API to build the URI, 
   # get entries, then add entries into the eventList
   for cal in config['Cals']:
      print cal
      entries = GetEntriesFromFeed(cal['URI_Parms'], config['num_days_to_search'])
      AddEntriesToEventList(entries, cal['cal_name'], cal['font_color'], eventList)

   # sort it based on delta (earliest first)
   eventList_sorted = sorted(eventList, key=lambda days: days[3])
   
   # next, build the list of lines to print.
   linesToPrint_list = []
   # for each event, build a line string, then add line plus font color to line
   # to print object, then add this to list of lines to print
   for event in eventList_sorted:
      # we only want events that are in the future, but no more than 90 days
      if (event[DELTA_SECS] > -1) and (event[DELTA_SECS] <= (config['num_days_to_search']*86400)):
         # if delta_secs is less than a day, print in hours
         if event[DELTA_SECS] > 86400:
            delta_days = round(event[DELTA_SECS]/86400.0)
            line = "%02dd: %s, %s (%s)" % (delta_days, event[TITLE], event[DATE_STR], event[TIME_STR])
         else:
            delta_hours = round(event[DELTA_SECS]/3600.0)
            line = "%02dh: %s, %s (%s)" % (delta_hours, event[TITLE], event[DATE_STR], event[TIME_STR])            
         lineToPrint = []
         lineToPrint.append(line)               # add TEXT_TO_PRINT
         lineToPrint.append(event[TEXT_COLOR])  # add FONT_COLOR
         linesToPrint_list.append(lineToPrint)
         print "Added (%s) - %s" % (event[CAL_NAME], line)
      else:
         line = "%02dd: %s, %s (%s)" % (event[DELTA_SECS], event[TITLE], event[DATE_STR], event[TIME_STR])
         print "Omitted (%s) - %s" % (event[CAL_NAME], line)
         
   # good links for PIL
   #http://infohost.nmt.edu/tcc/help/pubs/pil/index.html
   #http://effbot.org/imagingbook/image.htm#tag-Image.Image.save
   #http://www.pythonware.com/library/pil/handbook/imagedraw.htm
   #http://infohost.nmt.edu/tcc/help/pubs/pil/image-font.html - good font example
   #http://www.pythonware.com/library/pil/handbook/imagefont.htm
   #http://www.philomather.com/cal.png
      
   # load the font
   print "Loading font: %s" % config['font_path']
   arialFont  =  ImageFont.truetype ( config['font_path'], 16)
   
   # num lines to print
   linesToPrint = len(linesToPrint_list)

   for image in config['Images']:
      width  = image['width']
      height = image['height']

      if not isinstance(height, int):
         height = (linesToPrint * config['y_pitch'] + 5)

      # create an image object
      im = Image.new("RGB", (width, height), "rgb(215,215,215)")

      # extract a draw object for images
      draw_object = ImageDraw.Draw(im)

      # starting at the top, write out each line in the desired color 
      idx = 0
      for lineToPrint in linesToPrint_list:
         y_loc = 2 + (idx * config['y_pitch'])
         draw_object.text((2,y_loc), lineToPrint[TEXT_TO_PRINT], lineToPrint[FONT_COLOR], arialFont)
         idx+=1
      
      print "Saving cal image to %s" % image['path']
      im.save(image['path'])

if __name__ == '__main__':
   if len(sys.argv) != 2:
      print 'Usage: ./gcal_combiner path_to_config_json_file'
      sys.exit(1)
   #print sys.argv[1:]
   main(sys.argv[1:])

