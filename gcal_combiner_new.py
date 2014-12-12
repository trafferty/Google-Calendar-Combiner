#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2014 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Simple command-line sample for the Calendar API.
Command-line application that retrieves the list of the user's calendars."""

import sys

from oauth2client import client
from googleapiclient import sample_tools

def main(argv):
    # Authenticate and construct service.
    service, flags = sample_tools.init(
        argv, 'calendar', 'v3', __doc__, __file__,
        scope='https://www.googleapis.com/auth/calendar.readonly')

    print argv
    print __doc__
    print __file__
    try:
        page_token = None
        time_min='2014-12-01T23:00:00Z'
        time_max='2015-02-28T23:00:00Z'
        calendar_id_list = []

        while True:
            calendar_list = service.calendarList().list(pageToken=page_token).execute()
            for calendar_list_entry in calendar_list['items']:
                print("%s, %s" % (calendar_list_entry['summary'], calendar_list_entry['id']))
                calendar_id_list.append(calendar_list_entry['id'])
            page_token = calendar_list.get('nextPageToken')
            if not page_token:
                break

        combined_events = []
        if time.localtime().tm_isdst == 0:
            dst_adjust = 6
        else:
            dst_adjust = 5

        page_token = None
        for calendar_id in calendar_id_list:
            print(">>>>>>>>>> Events for calendar id: %s" % calendar_id)
            while True:
                events = service.events().list(calendarId=calendar_id, timeMax=time_max, timeMin=time_min, pageToken=page_token).execute()
                #events = service.events().list(calendarId='primary', timeMax=time_max, timeMin=time_min, pageToken=page_token).execute()
                for event in events['items']:
                    if 'summary' in event:
                        if 'dateTime' in event['start']:
                            dt = event['start']['dateTime']

                            
                            #print "Event %d: %s" % (i, dt)
                            event_start = dt[0:19]
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
                        elif 'date' in event['start']:
                            d = event['start']['date']
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


                        print("%s - %s" % (event['summary'], d))
                page_token = events.get('nextPageToken')
                if not page_token:
                    break


                for event in events['items']:
                    print event['summary']


                    item = event['items']



                    _event = []
                    _event.append(cal_data[2])          # add cal_name
                    _event.append(delta_secs)           # add DELTA_SECS
                    _event.append(an_event.title.text)  # add TITLE
                    _event.append(eventDate)            # add DATE_STR
                    _event.append(eventTime)            # add TIME_STR
                    # append to the event list
                    combined_events.append(_event)


    except client.AccessTokenRefreshError:
    print ('The credentials have been revoked or expired, please re-run'
      'the application to re-authorize.')

if __name__ == '__main__':
  main(sys.argv)
