# Go to: https://developers.google.com/calendar/quickstart/python
# Click on "Enable the Google Calendar API"
# Configure your OAuth client - select "Desktop app", then proceed
# Click on "Download Client Configuration" to obtain a credential.json file
# Do not share your credential.json file with anybody else.
# When app is run for the first time, you will need to sign in using your account.
# Allow the "View your calendars" permission request.

# Code adapted from https://developers.google.com/calendar/quickstart/python
from __future__ import print_function
from calendar import calendar
from multiprocessing.sharedctypes import Value
from re import L
from PyQt5 import QtGui, QtWidgets as qtw
import datetime
from datetime import date
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import json

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar']


def get_calendar_api(): #pragma: no cover
    """
    Get an object which allows you to consume the Google Calendar API.
    You do not need to worry about what this function exactly does, nor create test cases for it.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'): 
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build('calendar', 'v3', credentials=creds)

#Global api that are used for all transaction of events
global_api = get_calendar_api()

def get_upcoming_events(api, starting_time, number_of_events):
    """
    Shows basic usage of the Google Calendar API.
    Prints the start and name of the next n events on the user's calendar.
    """
    if (number_of_events <= 0):
        raise ValueError("Number of events must be at least 1.")
    
    events_result = api.events().list(calendarId='primary', timeMin=starting_time,
                                      maxResults=number_of_events, singleEvents=True,
                                      orderBy='startTime').execute()
    return events_result.get('items', [])

def get_all_events():
    events_result = global_api.events().list(calendarId='primary',
                                    singleEvents=True,
                                    orderBy='startTime').execute()
    return events_result.get('items', [])

def import_Event(service, txtfile):
    if(txtfile[-5:] != ".json"):
        raise Exception("Incorrect File extension")
    file = open(txtfile)
    event_list = json.load(file)
    if(len(event_list) <= 0):
        raise Exception("Empty Records of import File")

    for event in event_list:
        event = {
            'summary': event["summary"],  
            'location': event["location"],   
             'organizer': {
                 'email': event["organizer"].get("email"),
             },
            'start': {
                'dateTime': event["start"].get("dateTime") 
            },
            'end': {
                'dateTime': event["end"].get("dateTime")    
            },
            'description': event["description"],
            'status': event["status"],
            'attendees': event["attendees"],
            'iCalUID': event["iCalUID"]
            }
        service.events().import_(calendarId='primary', body=event).execute()
    
    

def export_event(eventList):
    if len(eventList) == 0:
        raise Exception("Empty List Provided")
    jsonObject = json.dumps(eventList,indent=4)
    with open('export.json','w') as outfile:
       outfile.write(jsonObject)


#Validates the date given
def validateDateFormat(date):
    isValid1 = True
    try:
        datetime.datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        isValid1 = False
        
    isValid2 = True
    try:
        datetime.datetime.strptime(date, "%d-%b-%Y")
    except ValueError:
        isValid2 = False

    return (isValid1 or isValid2)


#validate given address format
def addressValidation(address):
        address = address.split()
        valid = False
        if (len(address) > 1):
            valid = True
        return valid

#Change the event status from confirmed/tentatively etc.. to cancelled
def eventCancellation(service, eventID):
    event = {
        'status': 'cancelled'
    }
    service.events().patch(calendarId='primary', eventId=eventID, body=event).execute()
    print('Event Cancelled successfully')


class Attendees:
    def __init__(self, displayName, email, comment=None): #pragma: no cover
        self.displayName = displayName
        self.email = email
        self.comment = comment

class Calendar:
    def __init__(self, Title ,meetingType, startDate, startTime, endDate, endTime, address, status, attendeesList):

        if validateDateFormat(startDate) and validateDateFormat(endDate): #validate date string format
            #convert string format to uniform YYYY-mm-dd string format
            try:
                self.startDate = datetime.datetime.strptime(startDate,  '%d-%b-%Y').strftime('%Y-%m-%d') 
                self.startDate += 'T' + startTime + ":00Z"
                self.endDate = datetime.datetime.strptime(endDate,  '%d-%b-%Y').strftime('%Y-%m-%d') 
                self.endDate += 'T' + endTime + ":00Z"
            except ValueError:
                self.startDate = startDate + 'T' + startTime + ":00Z"
                self.endDate = endDate + 'T' + endTime + ":00Z"
        else:
            raise ValueError("Incorrect Date Format")

        self.Title = Title
        if (self.validateEventType(meetingType)):
            self.meetingType = meetingType
        else:
            raise ValueError("Incorrect Meeting Type")

        if (addressValidation(address)):
            self.address = address
        else:
            raise ValueError("Incorrect Address Format")

        self.status = status
        self.attendeesList = attendeesList

    def validateEventType(self, eventType):
        eventType = eventType.lower() #converts the input to lower case for comparison
        isValid = False
        if(eventType == "official meeting" or eventType == "online meeting" or eventType == "physical event"):
            isValid= True
        
        return isValid

    def add_event(self, service):
        if (len(self.attendeesList) > 20):
            raise Exception('Maximum number of attendees exceeded.')
        else:
            attendeesBody = [{'displayName':attendees.displayName,'email':attendees.email, 'comment':attendees.comment} for attendees in self.attendeesList]

        event = {
            'summary': self.Title,
            'description': self.meetingType,
            'location': self.address,
            'start': {
                'dateTime': self.startDate,
            },
            'end': {
                'dateTime': self.endDate,
            },
            'address' : self.address,
            'status' : self.status,
            'attendees' : attendeesBody,
            'guestsCanInviteOthers' : False,
            'guestsCanModify' : False,
        }

        addedEvent = service.events().insert(calendarId='primary', body=event, sendUpdates='all').execute()
        print('Event Added Successfully')
        
        return addedEvent

    def create_on_behalf(self, service, newOrganizer=None):  
        """ Creates a new event, organized by someone else """
        # validate inputs
        if (newOrganizer == None):
            raise Exception("No organizer provided.")
        
        validate_email(newOrganizer)
        
        # create event
        added = self.add_event(service)

        # change organizers
        service.events().move(
            calendarId='primary', eventId=added.get('id'), destination=newOrganizer, sendUpdates="all").execute()
    
    def change_organizer(self, service, eventId=None, newOwner=None):
        """ Changes the organizer of the event. """
        # input vaidation
        if(eventId is None) or (newOwner is None):
            raise Exception("Missing inputs.")
        
        validate_event_id(eventId)
        validate_email(newOwner)
        
        # change to new organizer
        service.events().move(
            calendarId='primary', eventId=eventId, destination=newOwner, sendUpdates = "all").execute()
        
    def update_event_title(self, service, eventId=None, newTitle=None):
        " Modifies the title of an event, given the event ID. "
        # input validation
        if (eventId is None) or (newTitle is None):
            raise Exception("Missing inputs.")
        
        validate_event_id(eventId)
        
        # changing title
        event = {
            'summary': newTitle
                }
        
        # executing the change
        service.events().patch(calendarId='primary', eventId=eventId, sendUpdates = 'all', body=event).execute()
        print('Title modified successfully')
        
    def update_event_dates(self, service, eventId=None, newStart=None, newEnd=None):
        """ Modifies the start and end dates of an event. """
        # validate inputs
        if (eventId is None) or (newStart is None) or (newEnd is None):
            raise Exception("Missing inputs.")
        
        if newStart > newEnd:
            raise Exception("Start Date cannot be after End Date.")
        
        validate_event_id(eventId)
        if (validateDateFormat(newStart)) and (validateDateFormat(newEnd)):
    
            # change
            event = {
                'start': {
                    'date': newStart,
                    'timeZone': 'America/Los_Angeles',
                },
                'end':{
                    'date': newEnd,
                    'timeZone': 'America/Los_Angeles',
                }
            }
            
            # execute change
            service.events().patch(
                calendarId='primary', eventId=eventId, sendUpdates = "all", body=event).execute()
    
    def get_attendees(self, service, eventId=None, count=None):
        """ Gets the emails of (count) number of attendees. """
        # input validation
        if (eventId is None) or (count is None):
            raise Exception("Missing inputs.")
        
        validate_event_id(eventId)
        
        # check count provided
        if 0 <= count <= 20:
            event = service.events().get(calendarId='primary', eventId=eventId).execute()
            attendees = event['attendees']
            
            info = []
            
            try:
                for attendee in range(count):
                    info.append(attendees[attendee]['email'])
            except:
                print("No more attendees.")
            
        # more than 20 attendees specified
        else:
            raise ValueError("Only 0 to 20 attendees are permitted per event.")
        
        return info
    
    def add_attendee(self, service, eventId=None, attendeeEmail=None, attendeeName=None):
        """ Adds an attendee from the event, given their email. """
        # validate inputs
        if (eventId is None) or (attendeeEmail is None) or (attendeeName is None):
            raise Exception("Missing inputs.")
        
        validate_email(attendeeEmail)
        validate_event_id(eventId)
        
        # get event
        event = service.events().get(calendarId='primary', eventId=eventId).execute()
        
        # get all existing attendees
        attendees = event['attendees']
        
        update = []
        
        for attendee in attendees:
            update.append(attendee)

        # add new attendee to event
        update.append({"email": attendeeEmail, "displayName": attendeeName, "responseStatus": "needsAction"})
        
        event = { 
            'attendees': update
            }
        
        # execute change
        service.events().patch(calendarId='primary', eventId=eventId, sendUpdates='all', body=event).execute()
    
    def delete_attendee(self, service, eventId=None, attendeeEmail=None):
        """ Removes an attendee from the event, given their email. """
        # validate inputs
        if (eventId is None) or (attendeeEmail is None):
            raise Exception("Missing inputs.")
        
        validate_email(attendeeEmail)
        validate_event_id(eventId)
        
        # get event
        event = service.events().get(calendarId='primary', eventId=eventId).execute()
        
        # get all existing attendees
        attendees = event['attendees']
        
        update = []
        
        # decide who is being removed
        for attendee in attendees:
            if attendee.get('email') != attendeeEmail:
                update.append(attendee)
                
        event = { 
            'attendees': update
            }

        # execute change
        service.events().patch(calendarId='primary', eventId=eventId, sendUpdates='all', body=event).execute()
        
        return attendeeEmail
    
    def update_attendee(self, service, eventId=None, oldAttendeeEmail=None, newAttendeeEmail=None):
        """ Updates attendee email. """
        # validate inputs
        if (eventId is None) or (oldAttendeeEmail is None) or (newAttendeeEmail is None):
            raise Exception("Missing inputs.")
        
        validate_event_id(eventId)
        validate_email(oldAttendeeEmail)
        validate_email(newAttendeeEmail)
        
        # get event
        event = service.events().get(calendarId='primary', eventId=eventId).execute()
        
        # get all existing attendees
        attendees = event['attendees']
        
        update = []
        
        # check info being updated
        for i in range(len(attendees)):
            if attendees[i]['email'] != oldAttendeeEmail:
                print(f"Appended: {attendees[i]['email']}")
                update.append({"email": attendees[i]['email']})
            else:
                print(f"Updated {attendees[i]['displayName']}")
                update.append({"email": newAttendeeEmail})

        print(update)
        
        event = { 
            'attendees': update
            }
        
        # execute change
        service.events().patch(calendarId='primary', eventId=eventId, sendUpdates='all', body=event).execute()
        
        return newAttendeeEmail
        
    def respond_invitation(self, service, eventId=None, email=None, response=None):
        """ Allows an attendee to respond to an invitation """
        # validation 
        if (eventId is None) or (email is None) or (response is None):
            raise Exception("Missing inputs.")
        
        if (response != "declined") and (response != "tentative") and (response != "accepted"):
            raise Exception("That's not a valid response.")
        
        validate_event_id(eventId)
        validate_email(email)
        
        # get event
        event = service.events().get(calendarId='primary', eventId=eventId).execute()
        
        # get all existing attendees
        attendees = event['attendees']
        
        update = []
        
        # decide who is being removed
        for attendee in attendees:
            if attendee.get('email') != email:
                update.append(attendee)
            else:
                update.append({"email": email, "responseStatus": response})
                
        event = { 
            'attendees': update
            }
        
        # execute change
        service.events().patch(calendarId='primary', eventId=eventId, sendUpdates='all', body=event).execute()
        
        return response
    
def view_events(service):
    """ Allows attendees to view events 5 years before and after the current date """
    # get current, past, and future date.
    current = datetime.datetime.now().utcnow().isoformat() + 'Z'
    past = str(str(int(current[:4])-5) + current[4:])
    future = str(str(int(current[:4])+5) + current[4:])
    
    # get events
    events_result = service.events().list(calendarId='primary', timeMin=past,
                                      timeMax=future, singleEvents=True,
                                      orderBy='startTime').execute()
    
    # as list
    eventsList = events_result.get('items', [])
    
    # print each event
    for event in eventsList:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary'], event['status'], ',Event ID : ' + event['id'])
        print(event['creator']['email'])
  
# validate common inputs      
def validate_email(email):
    if ("@" not in email) or (" " in email):
        raise ValueError("Invalid email provided.")
        
def validate_event_id(eventId):
    if (len(eventId) != 26) or (" " in eventId):
        raise ValueError("Invalid Event ID.")

class addAttendees_UI(qtw.QWidget):
    def __init__(self): #pragma: no cover
        super().__init__()
        self.attendeesList = []
        self.setWindowTitle('Add Attendees')
        self.setGeometry(0, 0, 400, 300)

        self.name = qtw.QLabel("Full Name : ",self)
        self.name.setFont(QtGui.QFont('Arial',9))
        self.name.move(85, 20)
        self.name.resize(80,20)

        self.name_field = qtw.QLineEdit(self)
        self.name_field.move(170,20)
        self.name_field.resize(150,20)

        self.email = qtw.QLabel("Email Address:",self)
        self.email.setFont(QtGui.QFont('Arial',9))
        self.email.move(85, 50)
        self.email.resize(80,20)

        self.email_field = qtw.QLineEdit(self)
        self.email_field.move(170,50)
        self.email_field.resize(150,20)

        self.comments = qtw.QLabel("Comments:",self)
        self.comments.setFont(QtGui.QFont('Arial',9))
        self.comments.move(85, 80)
        self.comments.resize(80,20)

        self.comments_field = qtw.QLineEdit(self)
        self.comments_field.move(170,80)
        self.comments_field.resize(150,20)

        self.attendeesButton = qtw.QPushButton("Add Attendees", self)
        self.attendeesButton.move(105,110)
        self.attendeesButton.resize(90,35)
        self.attendeesButton.clicked.connect(self.addAttendees)

    def addAttendees(self): #pragma: no cover
        attendees = Attendees(self.name_field.text(),self.email_field.text(),self.comments_field.text())
        self.attendeesList.append(attendees)

        msgBox = qtw.QMessageBox()
        msgBox.setIcon(qtw.QMessageBox.Information)
        msgBox.setText("Add more attendees?")
        msgBox.setWindowTitle("Add Attendees")
        msgBox.setStandardButtons(qtw.QMessageBox.Yes | qtw.QMessageBox.No)

        returnValue = msgBox.exec()
        if returnValue == qtw.QMessageBox.Yes:
            self.name_field.setText("")
            self.email_field.setText("")
            self.comments_field.setText("")
        else:
            self.close()

#All the UI and operation for creation of new event
class createEvent_UI(qtw.QWidget): 
    def __init__(self): #pragma: no cover
        super().__init__()
        self.setWindowTitle('Add an event')
        self.setGeometry(0, 0, 400, 300)

        self.title = qtw.QLabel("Event Title:",self)
        self.title.setFont(QtGui.QFont('Arial',9))
        self.title.move(85, 20)
        self.title.resize(80,20)

        self.title_field = qtw.QLineEdit(self)
        self.title_field.move(170,20)
        self.title_field.resize(150,20)

        self.title = qtw.QLabel("Event Type:",self)
        self.title.setFont(QtGui.QFont('Arial',9))
        self.title.move(85, 50)
        self.title.resize(80,20)

        self.type_field = qtw.QComboBox(self)
        self.type_field.addItems(["Official Meeting","Online Meeting","Physical Event"])
        self.type_field.move(170,50)
        self.type_field.resize(150,20)

        self.startDate = qtw.QLabel("Start Date:",self)
        self.startDate.setFont(QtGui.QFont('Arial',9))
        self.startDate.move(85, 80)
        self.startDate.resize(80,20)

        self.startField = qtw.QLineEdit(self)
        self.startField.move(170,80)
        self.startField.setPlaceholderText("YYYY-mm-dd or dd-Mon-YYYY")
        self.startField.resize(150,20)

        self.startTime = qtw.QLabel("Start Time:", self)
        self.startTime.setFont(QtGui.QFont('Arial',9))
        self.startTime.move(85, 110)
        self.startTime.resize(80,20)

        self.startHour = qtw.QLineEdit(self)
        self.startHour.move(170,110)
        self.startHour.setPlaceholderText("Hour")
        self.startHour.resize(50,20)

        self.startMinute = qtw.QLineEdit(self)
        self.startMinute.move(230,110)
        self.startMinute.setPlaceholderText("Minute")
        self.startMinute.resize(50,20)

        self.timeField = qtw.QComboBox(self)
        self.timeField.addItems(["AM","PM"])
        self.timeField.move(290,110)
        self.timeField.resize(50,20)

        self.endDate = qtw.QLabel("End Date:",self)
        self.endDate.setFont(QtGui.QFont('Arial',9))
        self.endDate.move(85, 140)
        self.endDate.resize(80,20)

        self.endField = qtw.QLineEdit(self)
        self.endField.move(170,140)
        self.endField.setPlaceholderText("YYYY-mm-dd or dd-Mon-YYYY")
        self.endField.resize(150,20)

        self.endTime = qtw.QLabel("End Time:", self)
        self.endTime.setFont(QtGui.QFont('Arial',9))
        self.endTime.move(85, 170)
        self.endTime.resize(80,20)

        self.endHour = qtw.QLineEdit(self)
        self.endHour.move(170,170)
        self.endHour.setPlaceholderText("Hour")
        self.endHour.resize(50,20)

        self.endMinute = qtw.QLineEdit(self)
        self.endMinute.move(230,170)
        self.endMinute.setPlaceholderText("Minute")
        self.endMinute.resize(50,20)

        self.timeField2 = qtw.QComboBox(self)
        self.timeField2.addItems(["AM","PM"])
        self.timeField2.move(290,170)
        self.timeField2.resize(50,20)

        self.lblLocation = qtw.QLabel("Venue : ",self)
        self.lblLocation.setFont(QtGui.QFont('Arial',9))
        self.lblLocation.move(85, 200)
        self.lblLocation.resize(80,20)

        self.locationField = qtw.QLineEdit(self)
        self.locationField.move(170,200)
        self.locationField.setPlaceholderText("Address of Venue")
        self.locationField.resize(150,20)

        self.attendeesButton = qtw.QPushButton("Add Attendees", self)
        self.attendeesButton.move(105,230)
        self.attendeesButton.resize(100,35)
        self.attendeesButton.clicked.connect(self.addAttendees)

        self.createButton = qtw.QPushButton("Create Event", self)
        self.createButton.move(210,230)
        self.createButton.resize(100,35)
        self.createButton.clicked.connect(self.createEvent)

    def addAttendees(self): #pragma: no cover
        self.attendeesWindow = addAttendees_UI()
        self.attendeesWindow.show()
    
    def createEvent(self): #pragma: no cover
        try:
            attendeesList = self.attendeesWindow.attendeesList
        except AttributeError:
            qtw.QMessageBox.about(self, "Empty Attendees Record", "Please Add Attendees to the event.")
            return

        if(self.validateTime(self.startHour.text(),self.startMinute.text()) and self.validateTime(self.endHour.text(),self.endMinute.text())):

            startHour = self.startHour.text()
            endHour = self.endHour.text()
        else:
            qtw.QMessageBox.about(self, "Invalid Event Time", "Please enter Valid Event Time.")
            return

        if(self.timeField.currentText() == "AM" and startHour == "12"):
            startHour = "00"
        if(self.timeField.currentText() == "AM" and endHour == "12"):
            endHour = "00"

        startTime = startHour + ":" + self.startMinute.text()
        endTime = endHour + ":" + self.endMinute.text()
        
        if(self.timeField.currentText() == 'PM'):
            if (self.startHour.text() != "12"):
                startHour = int(self.startHour.text()) + 12
            
            startTime = str(startHour) + ":" + self.startMinute.text()
        if(self.timeField2.currentText() == 'PM' and self.endHour.text() != "12"):
            endHour = int(self.endHour.text()) + 12
            endTime = str(endHour) + ":" + self.endMinute.text()
        
        calendar = Calendar(self.title_field.text(),self.type_field.currentText(),self.startField.text(), startTime,
        self.endField.text(), endTime ,self.locationField.text(),"confirmed",attendeesList)
        calendar.add_event(global_api)
    
    def validateTime(self, hour, minute): #pragma: no cover
        valid = False
        hourValidate = QtGui.QIntValidator()
        hourValidate.setRange(0,12)
        hourValidate.validate(hour,0)

        minuteValidate = QtGui.QIntValidator()
        minuteValidate.setRange(0,60)

        if(minuteValidate.validate(minute,0)[0] == QtGui.QValidator.State.Acceptable
        and hourValidate.validate(hour,0)[0] == QtGui.QValidator.State.Acceptable):
            valid = True
        
        if not valid: #if the format is not valid raise error
            raise ValueError("Incorrect Time format")

        return valid

class viewEvent_UI(qtw.QWidget):
    def __init__(self): #pragma: no cover
        super().__init__()
        self.setWindowTitle('View event')
        self.setGeometry(0, 0, 900, 300)
        self.createTable()

        # Add box layout, add table to box layout and add box layout to widget
        self.layout = qtw.QVBoxLayout()
        self.layout.addWidget(self.tableWidget) 
        self.setLayout(self.layout) 

        # Show widget
        self.show()

    def createTable(self): #pragma: no cover
        self.tableWidget = qtw.QTableWidget()

        self.tableWidget.resizeColumnsToContents()
        events = get_all_events()
        #time_now = datetime.datetime.utcnow().isoformat() + 'Z' 
        #events = get_upcoming_events(global_api,time_now,10)
        self.tableWidget.setColumnCount(6)
        self.tableWidget.setRowCount(len(events))
        self.tableWidget.setHorizontalHeaderLabels(["Event ID","Event Title","Event Venue","Attendees","Start Date","End Date"])

        #Loop through the records of events
        for records in range(0,len(events)):
            attendees = ""
            attendeesList = events[records]['attendees']
            for i in attendeesList:
                try:
                    attendees += i['displayName'] + ", "
                except KeyError:
                    attendees = ""
            try:
                self.tableWidget.setItem(records,0, qtw.QTableWidgetItem(events[records]['id']))
                self.tableWidget.setItem(records,1, qtw.QTableWidgetItem(events[records]['summary']))
                self.tableWidget.setItem(records,2, qtw.QTableWidgetItem(events[records]['location']))
                self.tableWidget.setItem(records,3, qtw.QTableWidgetItem(attendees))          
                self.tableWidget.setItem(records,4, qtw.QTableWidgetItem(events[records]['start'].get('dateTime')))
                self.tableWidget.setItem(records,5, qtw.QTableWidgetItem(events[records]['end'].get('dateTime')))
            except KeyError:
                pass
        
        #Resize table content
        self.resizeTable()

    def resizeTable(self): #pragma: no cover
        #Resize the table to follow content size
        header = self.tableWidget.horizontalHeader()
        header.setSectionResizeMode(0,qtw.QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1,qtw.QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2,qtw.QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3,qtw.QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4,qtw.QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5,qtw.QHeaderView.ResizeMode.ResizeToContents)

class searchResult_UI(qtw.QWidget):
    def __init__(self): #pragma: no cover
        super().__init__()
        self.setWindowTitle('View event')
        self.setGeometry(0, 0, 900, 300)
        self.events = []
        

    def createTable(self):#pragma: no cover
        self.tableWidget = qtw.QTableWidget()

        self.tableWidget.resizeColumnsToContents()
        events = self.events
        self.tableWidget.setColumnCount(6)
        self.tableWidget.setRowCount(len(events))
        self.tableWidget.setHorizontalHeaderLabels(["Event ID","Event Title","Event Venue","Attendees","Start Date","End Date"])

        #Loop through the records of events
        for records in range(0,len(events)):
            attendees = ""
            attendeesList = events[records]['attendees']
            for i in attendeesList:
                try:
                    attendees += i['displayName'] + ", "
                except KeyError:
                    attendees = ""
            try:
                self.tableWidget.setItem(records,0, qtw.QTableWidgetItem(events[records]['id']))
                self.tableWidget.setItem(records,1, qtw.QTableWidgetItem(events[records]['summary']))
                self.tableWidget.setItem(records,2, qtw.QTableWidgetItem(events[records]['location']))
                self.tableWidget.setItem(records,3, qtw.QTableWidgetItem(attendees))          
                self.tableWidget.setItem(records,4, qtw.QTableWidgetItem(events[records]['start'].get('dateTime')))
                self.tableWidget.setItem(records,5, qtw.QTableWidgetItem(events[records]['end'].get('dateTime')))
            except KeyError:
                pass
        
        #Resize table content
        self.resizeTable()
        # Add box layout, add table to box layout and add box layout to widget
        self.layout = qtw.QVBoxLayout()
        self.layout.addWidget(self.tableWidget) 
        self.setLayout(self.layout) 

    def resizeTable(self):#pragma: no cover
        #Resize the table to follow content size
        header = self.tableWidget.horizontalHeader()
        header.setSectionResizeMode(0,qtw.QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1,qtw.QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2,qtw.QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3,qtw.QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4,qtw.QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5,qtw.QHeaderView.ResizeMode.ResizeToContents)

class searchEvent_UI(qtw.QWidget):
    def __init__(self): #pragma: no cover
        super().__init__()
        self.setWindowTitle('Search event')
        self.setGeometry(0, 0, 400, 300)
        self.filtered_event = []

        self.title = qtw.QLabel("Event Title:",self)
        self.title.setFont(QtGui.QFont('Arial',9))
        self.title.move(85, 20)
        self.title.resize(80,20)

        self.title_field = qtw.QLineEdit(self)
        self.title_field.move(170,20)
        self.title_field.resize(150,20)

        self.title = qtw.QLabel("Event Type:",self)
        self.title.setFont(QtGui.QFont('Arial',9))
        self.title.move(85, 50)
        self.title.resize(80,20)

        self.type_field = qtw.QComboBox(self)
        self.type_field.addItems(["","Official Meeting","Online Meeting","Physical Event"])
        self.type_field.move(170,50)
        self.type_field.resize(150,20)

        self.year = qtw.QLabel("Year:",self)
        self.year.setFont(QtGui.QFont('Arial',9))
        self.year.move(85, 80)
        self.year.resize(80,20)

        self.yearField = qtw.QLineEdit(self)
        self.yearField.move(170,80)
        self.yearField.setPlaceholderText("YYYY")
        self.yearField.resize(150,20)

        self.month = qtw.QLabel("Month:",self)
        self.month.setFont(QtGui.QFont('Arial',9))
        self.month.move(85, 110)
        self.month.resize(80,20)

        self.MonthField = qtw.QComboBox(self)
        self.MonthField.move(170,110)
        self.MonthField.addItems(["","01","02","03","04","05","06","07","08","09","10","11","12"])
        self.MonthField.resize(80,20)

        self.day = qtw.QLabel("Day: ",self)
        self.day.setFont(QtGui.QFont('Arial',9))
        self.day.move(85, 140)
        self.day.resize(80,20)

        self.dayField = qtw.QLineEdit(self)
        self.dayField.move(170,140)
        self.dayField.setPlaceholderText("Day")
        self.dayField.resize(150,20)

        self.lblLocation = qtw.QLabel("Venue : ",self)
        self.lblLocation.setFont(QtGui.QFont('Arial',9))
        self.lblLocation.move(85, 170)
        self.lblLocation.resize(80,20)

        self.locationField = qtw.QLineEdit(self)
        self.locationField.move(170,170)
        self.locationField.setPlaceholderText("Address of Venue")
        self.locationField.resize(150,20)

        self.searchButton = qtw.QPushButton("Search Records", self)
        self.searchButton.move(190,200)
        self.searchButton.resize(100,35)
        self.searchButton.clicked.connect(self.searchEvent)

        self.searchButton = qtw.QPushButton("Export Event", self)
        self.searchButton.move(85,200)
        self.searchButton.resize(100,35)
        self.searchButton.clicked.connect(self.exportEvent)

    def searchEvent(self): # pragma: no cover
        events = get_all_events()
        
        for event in events:
            title = self.title_field.text()
            eventType = self.type_field.currentText()
            location = self.locationField.text()
            day = self.dayField.text()
            month = self.MonthField.currentText()
            year = self.yearField.text()
            try:
                if(title in event['summary'] and eventType in event['description'] and
                 location in event['location']):
                    startDate = event['start'].get('dateTime')
                    endDate = event['end'].get('dateTime')
                    if(startDate is not None):
                        startYear = startDate[:4]
                        endYear = endDate[:4]
                        startMonth = startDate[5:7]
                        endMonth = endDate[5:7]
                        startDay = startDate[8:10]
                        endDay = endDate[8:10]
                        if(day in startDay and month in startMonth and year in startYear) or (day in endDay and month in endMonth and year in endYear):
                            self.filtered_event.append(event)
            except KeyError:
                pass
        self.searchResult = searchResult_UI()
        self.searchResult.events = self.filtered_event
        self.searchResult.createTable()
        
        self.searchResult.show()
    
    def exportEvent(self): #pragma: no cover
        eventList = self.filtered_event
        if len(eventList) != 0:
            export_event(eventList)
            qtw.QMessageBox.about(self, "Export Done", "Event Exported Successfully.")
        else:
            qtw.QMessageBox.about(self, "No records", "Search for a event First.")

class deleteEvent_UI(qtw.QWidget):
    def __init__(self): #pragma: no cover
        super().__init__()
        self.setWindowTitle('Delete an event')
        self.setGeometry(0, 0, 400, 300)

        self.searchLbl = qtw.QLabel("Enter Event ID:",self)
        self.searchLbl.setFont(QtGui.QFont('Arial',9))
        self.searchLbl.move(85, 20)
        self.searchLbl.resize(80,20)

        self.id_field = qtw.QLineEdit(self)
        self.id_field.move(170,20)
        self.id_field.resize(150,20)

        self.deleteBtn = qtw.QPushButton("Delete Event", self)
        self.deleteBtn.move(165,70)
        self.deleteBtn.resize(70,25)
        self.deleteBtn.clicked.connect(self.deleteEvent)

    def deleteEvent(self): #pragma: no cover
        time_now = datetime.datetime.utcnow().isoformat() + 'Z' 
        evt_ID = self.id_field.text()
        event = global_api.events().get(calendarId='primary', eventId = evt_ID).execute()
        if not event:
            qtw.QMessageBox.about(self, "No Records", "No Event Records Found. Please Check Again")
        else:
            endDate = event['end'].get('dateTime')
            if (endDate > time_now):
                qtw.QMessageBox.about(self, "Deletion Prohibited","Cannot Delete events that have not yet passed.")
            else:
                global_api.events().delete(calendarId='primary', eventId= evt_ID).execute()


class importEvent_UI(qtw.QWidget):
    def __init__(self): #pragma: no cover
        super().__init__()
        self.setWindowTitle('Delete an event')
        self.setGeometry(0, 0, 400, 300)
        self.filepath = ""

        self.File = qtw.QLabel("File Name:",self)
        self.File.setFont(QtGui.QFont('Arial',9))
        self.File.move(85, 20)
        self.File.resize(80,20)

        self.name_field = qtw.QLineEdit(self)
        self.name_field.move(170,20)
        self.name_field.resize(150,20)

        self.fileBtn = qtw.QPushButton("Select File", self)
        self.fileBtn.move(125,70)
        self.fileBtn.resize(70,25)
        self.fileBtn.clicked.connect(self.selectFile)

        self.importBtn = qtw.QPushButton("Import File", self)
        self.importBtn.move(200,70)
        self.importBtn.resize(70,25)
        self.importBtn.clicked.connect(self.importFile)

    def selectFile(self): #pragma: no cover
        self.filepath = qtw.QFileDialog.getOpenFileName(self, 'Open file')
        self.name_field.setText(self.filepath[0])
        txt = self.filepath[0]

    def importFile(self): #pragma: no cover
        if len(self.filepath) != 0:
            import_Event(global_api,self.filepath[0])
            qtw.QMessageBox.about(self, "Import Done", "Imported Successfully.")
        else:
            qtw.QMessageBox.about(self, "No Records", "No Event Records Found. Please Check Again")


#Controlling UI for the whole program
class Main_UI(qtw.QWidget): 
    def __init__(self): #pragma: no cover
        super().__init__()
        self.setWindowTitle('Main UI')
        self.email = ""
        self.setGeometry(0, 0, 300, 400)

        self.createButton = qtw.QPushButton("Add Event", self)
        self.createButton.move(105,60)
        self.createButton.resize(90,35)
        self.createButton.clicked.connect(self.addEvent)

        self.viewButton = qtw.QPushButton("View Events", self)
        self.viewButton.move(105,100)
        self.viewButton.resize(90,35)
        self.viewButton.clicked.connect(self.viewEvent)

        self.searchButton = qtw.QPushButton("Search Events", self)
        self.searchButton.move(105,140)
        self.searchButton.resize(90,35)
        self.searchButton.clicked.connect(self.searchEvent)

        self.deleteButton = qtw.QPushButton("Delete Events", self)
        self.deleteButton.move(105,180)
        self.deleteButton.resize(90,35)
        self.deleteButton.clicked.connect(self.deleteEvent)

        self.importButton = qtw.QPushButton("Import Events", self)
        self.importButton.move(105,220)
        self.importButton.resize(90,35)
        self.importButton.clicked.connect(self.importEvent)

        self.show()

    def addEvent(self): #pragma: no cover
        self.createWindow = createEvent_UI()
        self.createWindow.show()
    
    def viewEvent(self): #pragma: no cover
        self.createWindow = viewEvent_UI()
        self.createWindow.show()
    
    def searchEvent(self): #pragma: no cover
        self.createWindow = searchEvent_UI()
        self.createWindow.show()
     
    def deleteEvent(self): #pragma: no cover
        self.createWindow = deleteEvent_UI()
        self.createWindow.show()
    
    def importEvent(self): #pragma: no cover
        self.createWindow = importEvent_UI()
        self.createWindow.show()

#Login page for email to verify event organizer either true/false
class Login_UI(qtw.QWidget):
    def __init__(self): #pragma: no cover
        super().__init__()
        self.setWindowTitle('Login UI')
        self.setGeometry(0, 0, 600, 300)
          

        self.label_1 = qtw.QLabel("Email:",self)
        
        self.label_1.setFont(QtGui.QFont('Helvetica',12))
        self.label_1.move(180, 100)

        self.email_field = qtw.QLineEdit(self)
        self.email_field.move(260,100)
        self.email_field.resize(150,20)
        self.login = qtw.QPushButton("Login", self)
        self.login.move(250,220)
        self.login.resize(100,40)
        self.login.clicked.connect(self.openMainWindow)

        self.show()

    def openMainWindow(self): #pragma: no cover
        self.close()
        self.MainWindow = Main_UI()
        self.MainWindow.email = self.email_field.text()
        self.MainWindow.show()

    def openMainWindow(self): #pragma: no cover
        self.close()
        self.MainWindow = Main_UI()
        self.MainWindow.email = self.email_field.text()
        self.MainWindow.show()

def main(): #pragma: no cover
    api = get_calendar_api()
    
    time_now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    
    events = get_upcoming_events(api, time_now, 10)
    
    # display upcoming events
    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary'], event['status'], ',Event ID : ' + event['id'])
    
    # launch UI
    app = qtw.QApplication([])
    UI = Main_UI()
    app.exec_()

if __name__ == "__main__":  # Prevents the main() function from being called by the test suite runner
    main()


