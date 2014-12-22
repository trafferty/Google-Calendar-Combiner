# cd ~/src/github/google-api-python-client/samples/calendar_api

import sys
import argparse
import httplib2
import os
import time

from googleapiclient import discovery
from oauth2client import client
from oauth2client import file
from oauth2client import tools
from oauth2client.file import Storage

# Enums for the event object:
# ['cal_name', delta_sec, 'event_title', 'event_date', 'event_time']
CAL_NAME, DELTA_SECS, TITLE, DATE_STR, TIME_STR = range(5)

def getAPIservice(args, name, version, client_secrets_file, scope=None, parents=[], discovery_filename=None):
    """A common initialization routine for samples.

    Many of the sample applications do the same initialization, which has now
    been consolidated into this function. This function uses common idioms found
    in almost all the samples, i.e. for an API with name 'apiname', the
    credentials are stored in a file named apiname.dat, and the
    client_secrets.json file is stored in the same directory as the application
    main file.

    Args:
    argv: list of string, the command-line parameters of the application.
    name: string, name of the API.
    version: string, version of the API.
    doc: string, description of the application. Usually set to __doc__.
    file: string, filename of the application. Usually set to __file__.
    parents: list of argparse.ArgumentParser, additional command-line flags.
    scope: string, The OAuth scope used.
    discovery_filename: string, name of local discovery file (JSON). Use when discovery doc not available via URL.

    Returns:
    A tuple of (service, flags), where service is the service object and flags
    is the parsed command-line flags.
    """
    if scope is None:
        scope = 'https://www.googleapis.com/auth/' + name

    # Parser command-line arguments.
    parent_parsers = [tools.argparser]
    parent_parsers.extend(parents)
    parser = argparse.ArgumentParser(
      description="Google API v3 Service Provider",
      formatter_class=argparse.RawDescriptionHelpFormatter,
      parents=parent_parsers)
    flags = parser.parse_args(args)
    print("args = %s" % (args))

    # Name of a file containing the OAuth 2.0 information for this
    # application, including client_id and client_secret, which are found
    # on the API Access tab on the Google APIs
    # Console <http://code.google.com/apis/console>.
    # client_secrets = os.path.join(os.path.dirname(filename),
    #                             'client_secrets.json')

    # Set up a Flow object to be used if we need to authenticate.
    flow = client.flow_from_clientsecrets(client_secrets_file,
      scope=scope,
      message=tools.message_if_missing(client_secrets_file))

    # Prepare credentials, and authorize HTTP object with them.
    # If the credentials don't exist or are invalid run through the native client
    # flow. The Storage object will ensure that if successful the good
    # credentials will get written back to a file.
    storage = file.Storage(name + '.dat')
    credentials = storage.get()
    if credentials is None or credentials.invalid:
        credentials = tools.run_flow(flow, storage, flags)
    http = credentials.authorize(http = httplib2.Http())

    if discovery_filename is None:
        # Construct a service object via the discovery service.
        service = discovery.build(name, version, http=http)
    else:
        # Construct a service object using a local discovery document file.
        with open(discovery_filename) as discovery_file:
          service = discovery.build_from_document(
              discovery_file.read(),
              base='https://www.googleapis.com/',
              http=http)
    return (service, flags)

if 0:
    from googleapiclient import sample_tools
    argv = ['test.py']
    doc = "Simple command-line sample for the Calendar API."
    file = "test.py"

    service, flags = sample_tools.init(
        argv, 'calendar', 'v3', doc, file,
        scope='https://www.googleapis.com/auth/calendar.readonly')
else:
    args = []
    client_secrets_file = os.path.join(os.path.dirname('test.py'),
                                'client_secrets.json')

    service, flags = getAPIservice(
        args, 'calendar', 'v3', client_secrets_file,
        scope='https://www.googleapis.com/auth/calendar.readonly')
    

page_token = None
time_min='2014-12-01T23:00:00Z'
time_max='2015-02-28T23:00:00Z'
calendar_id_list = []

# while True:
#     calendar_list = service.calendarList().list(pageToken=page_token).execute()
#     for calendar_list_entry in calendar_list['items']:
#         print("%s, %s" % (calendar_list_entry['summary'], calendar_list_entry['id']))
#         calendar_id_list.append(calendar_list_entry['id'])
#     page_token = calendar_list.get('nextPageToken')
#     if not page_token:
#         break

combined_events = []
if time.localtime().tm_isdst == 0:
    dst_adjust = 6
else:
    print "Times will be adjusted for daylight savings time"
    dst_adjust = 5
now_ts = time.mktime(time.gmtime(time.time()))

page_token = None
calendar_id_list.append(u'ts87a0uvmltvnr3o7d7kh8vh9a3i5el7@import.calendar.google.com')
calendar_id_list.append(u'3en3c0r18aubc8jhdds2ba27u499lo7o@import.calendar.google.com')
calendar_id_list.append(u'mleu1end2d2pf2vqs5l0umtsvreq0bi7@import.calendar.google.com')
calendar_id_list.append(u'fjtausch@gmail.com')
calendar_id_list.append(u'qmte51ju2ppoe5vulg7ruug2b4@group.calendar.google.com')
calendar_id_list.append(u'tom.rafferty@briggo.com')
calendar_id_list.append(u'thomasrafferty@gmail.com')
calendar_id_list.append(u'#contacts@group.v.calendar.google.com')
calendar_id_list.append(u'en.usa#holiday@group.v.calendar.google.com')


# print(">>>>>>>>>> Events for calendar id: %s" % calendar_id)
# while True:
#     events = service.events().list(calendarId=calendar_id, timeMax=time_max, timeMin=time_min, pageToken=page_token).execute()
#     #events = service.events().list(calendarId='primary', timeMax=time_max, timeMin=time_min, pageToken=page_token).execute()
#     for event in events['items']:
#         #if 'summary' in event:
#             #combined_events.append(event)
#             #print("%s - %s" % (event['summary'], ""))
#     page_token = events.get('nextPageToken')
#     if not page_token:
#         break

if 1:
    for calendar_id in calendar_id_list:
        print(">>>>>>>>>> Events for calendar id: %s" % calendar_id)
        while True:
            events = service.events().list(calendarId=calendar_id, timeMax=time_max, timeMin=time_min, pageToken=page_token).execute()
            #events = service.events().list(calendarId='primary', timeMax=time_max, timeMin=time_min, pageToken=page_token).execute()
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
                    new_event.append(calendar_id)          # add cal_name
                    new_event.append(delta_secs)           # add DELTA_SECS
                    new_event.append(event['summary'])     # add TITLE
                    new_event.append(eventDate)            # add DATE_STR
                    new_event.append(eventTime)            # add TIME_STR
                    # append to the event list
                    combined_events.append(new_event)

            page_token = events.get('nextPageToken')
            if not page_token:
                break

print '*********************************************************'
print "Fetched data from %d calendars:" % len(calendar_id_list)

#print combined_events

# sort it based on delta (earliest first)
eventList_sorted = sorted(combined_events, key=lambda x: x[1])
#combined_events.sort(key=lambda x: x[1])

linesToPrint = []
days_in_future=90
# next, build the list of lines to print.
# for each event, build a line string, then add line plus cal_name to list
# of lines to print
for event in eventList_sorted:
 if (event[DELTA_SECS] > -1) and (event[DELTA_SECS] <= (days_in_future*86400)):
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


