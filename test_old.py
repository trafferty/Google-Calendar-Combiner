import httplib2
import sys
import argparse

from apiclient.discovery import build
from oauth2client.file import Storage
from oauth2client.client import AccessTokenRefreshError
from oauth2client.client import OAuth2WebServerFlow
from oauth2client import tools
from oauth2client.tools import run
from oauth2client.tools import run_flow

client_id = "376895794675-u5eq71ega3cl8l7vgsvq1j5jdng66css.apps.googleusercontent.com"
client_secret = "ldUOxKJ1ttwyA73s_yYHlchQ"
scope = 'https://www.googleapis.com/auth/calendar'
flow = OAuth2WebServerFlow(client_id, client_secret, scope)

storage = Storage('credentials.dat')

credentials = storage.get()

parser = argparse.ArgumentParser(parents=[tools.argparser])
flags = parser.parse_args()

if credentials is None or credentials.invalid:
    credentials = tools.run_flow(flow, storage, flags)

http = httplib2.Http()
http = credentials.authorize(http)

# The apiclient.discovery.build() function returns an instance of an API service
# object can be used to make API calls. The object is constructed with
# methods specific to the calendar API. The arguments provided are:
#   name of the API ('calendar')
#   version of the API you are using ('v3')
#   authorized httplib2.Http() object that can be used for API calls
service = build('calendar', 'v3', http=http)

try:
    # The Calendar API's events().list method returns paginated results, so we
    # have to execute the request in a paging loop. First, build the
    # request object. The arguments provided are:
    #   primary calendar for user
    request = service.events().list(calendarId='thomasrafferty@gmail.com')
    # Loop until all pages have been processed.
    while request != None:
        # Get the next page.
        response = request.execute()
        # Accessing the response like a dict object with an 'items' key
        # returns a list of item objects (events).
        for event in response.get('items', []):
            # The event object is a dict object with a 'summary' key.
            print repr(event.get('summary', 'NO SUMMARY')) + '\n'
        # Get the next request object by passing the previous request object to
        # the list_next method.
        request = service.events().list_next(request, response)

except AccessTokenRefreshError:
    # The AccessTokenRefreshError exception is raised if the credentials
    # have been revoked by the user or they have expired.
    print ('The credentials have been revoked or expired, please re-run'
       'the application to re-authorize')
