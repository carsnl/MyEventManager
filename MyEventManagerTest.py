from calendar import Calendar
import unittest
from unittest.mock import MagicMock, Mock, patch
import MyEventManager
from MyEventManager import *
# Add other imports here if needed

class MyEventManagerTest(unittest.TestCase):
    # This test tests number of upcoming events.
    def test_get_upcoming_events_number(self):
        """ Tests get_upcoming_events, tests number of upcoming events."""
        # valid
        # TC1
        num_events = 1
        time = "2020-08-03T00:00:00.000000Z"

        mock_api = Mock()
        events = MyEventManager.get_upcoming_events(mock_api, time, num_events)

        self.assertEqual(
            mock_api.events.return_value.list.return_value.execute.return_value.get.call_count, 1)

        args, kwargs = mock_api.events.return_value.list.call_args_list[0]

        self.assertEqual(kwargs['maxResults'], num_events)
        
        # valid
        # TC2
        num_events = -1
        time = "2020-08-03T00:00:00.000000Z"

        with self.assertRaises(ValueError):
            events = MyEventManager.get_upcoming_events(mock_api, time, num_events)
        
        # invalid 
        # TC3
        num_events = 0
        time = "2020-08-03T00:00:00.000000Z"
        
        with self.assertRaises(ValueError):
            events = MyEventManager.get_upcoming_events(mock_api, time, num_events)

    def test_validate_date_format(self):
        """ Tests validateDateFormat. Returns a boolean depending on a provided date format. """
        #Test validate_dateFormat
        attendees = [Attendees("John","jsmith@gmail.com")]

        #TC1
        Calendar("An event", "Official Meeting",'10-OCT-2022','08:00','10-OCT-2022','08:00', 
                      "123 Fake Street Clayton VIC 3400", "confirmed", attendees)
        #TC2
        Calendar("An event", "Official Meeting",'2022-10-10','08:00','2022-10-10','08:00', 
                      "123 Fake Street Clayton VIC 3400", "confirmed", attendees)
        
        #TC3
        with self.assertRaises(ValueError):
            Calendar("An event", "Official Meeting",'abc','08:00','10-OCT-2022','08:00', 
                      "123 Fake Street Clayton VIC 3400", "confirmed", attendees)
        
        with self.assertRaises(ValueError):
            Calendar("An event", "Official Meeting",'10-10-2022','08:00','10-10-2022','08:00', 
                      "123 Fake Street Clayton VIC 3400", "confirmed", attendees)
        
        with self.assertRaises(ValueError):
            Calendar("An event", "Official Meeting",'123','08:00','123','08:00', 
                      "123 Fake Street Clayton VIC 3400", "confirmed", attendees)
        
        with self.assertRaises(ValueError):
            Calendar("An event", "Official Meeting",'','08:00','','08:00', 
                      "123 Fake Street Clayton VIC 3400", "confirmed", attendees)
    
    def test_valid_eventType(self):
        """ Tests validateEventType. Returns a boolean depending on a provided event type."""
        with self.assertRaises(ValueError):
            attendees = [Attendees("John","jsmith@gmail.com")]
            Calendar("An event", "Meeting",'2022-10-10','08:00','2022-10-10','08:00', 
                      "123 Fake Street Clayton VIC 3400", "confirmed", attendees)
        
        with self.assertRaises(ValueError):
            attendees = [Attendees("John","jsmith@gmail.com")]
            Calendar("An event", "",'2022-10-10','08:00','2022-10-10','08:00', 
                      "123 Fake Street Clayton VIC 3400", "confirmed", attendees)

    def test_address_validation(self):
        """ Tests addressValidation. Returns a boolean depending on a provided address format."""
        with self.assertRaises(ValueError):
            attendees = [Attendees("John","jsmith@gmail.com")]
            Calendar("An event", "Official Meeting",'2022-10-10','08:00','2022-10-10','08:00', 
                      "", "confirmed", attendees)
        with self.assertRaises(ValueError):
            attendees = [Attendees("John","jsmith@gmail.com")]
            Calendar("An event", "Official Meeting",'2022-10-10','08:00','2022-10-10','08:00', 
                      "123", "confirmed", attendees)
    
    def test_max_attendees(self):
        """ Tests if the program raises an Exception if there are over 20 attendees to an event. """
        mock_api = MagicMock()
        with self.assertRaises(Exception):
            attendees = [Attendees("John","jsmith@gmail.com"),Attendees("John","jsmith@gmail.com"),Attendees("John","jsmith@gmail.com"),
                        Attendees("John","jsmith@gmail.com"),Attendees("John","jsmith@gmail.com"),Attendees("John","jsmith@gmail.com"),
                        Attendees("John","jsmith@gmail.com"),Attendees("John","jsmith@gmail.com"),Attendees("John","jsmith@gmail.com"),
                        Attendees("John","jsmith@gmail.com"),Attendees("John","jsmith@gmail.com"),Attendees("John","jsmith@gmail.com"),
                        Attendees("John","jsmith@gmail.com"),Attendees("John","jsmith@gmail.com"),Attendees("John","jsmith@gmail.com"),
                        Attendees("John","jsmith@gmail.com"),Attendees("John","jsmith@gmail.com"),Attendees("John","jsmith@gmail.com"),
                        Attendees("John","jsmith@gmail.com"),Attendees("John","jsmith@gmail.com"),Attendees("John","jsmith@gmail.com"),
                        Attendees("John","jsmith@gmail.com"),Attendees("John","jsmith@gmail.com"),Attendees("John","jsmith@gmail.com"),
                        Attendees("John","jsmith@gmail.com"),Attendees("John","jsmith@gmail.com"),Attendees("John","jsmith@gmail.com"),
            ]
            event = Calendar("An event", "Official Meeting",'2022-10-10','08:00','2022-10-10','08:00', 
                      "123 Fake Street Clayton VIC 3400", "confirmed", attendees)
            event.add_event(mock_api)

    def test_create_on_behalf(self):
        """ Tests create_on_behalf(). Tests if an event was successfully created on someone's behalf. """
        # mock api
        mock_api = MagicMock()

        # create event 
        attendees = [Attendees("John","jsmith@gmail.com")]
        event = Calendar("An event", "Official Meeting",'2022-10-10','08:00','2022-10-10','08:00', 
                      "123 Fake Street Clayton VIC 3400", "confirmed", attendees)
        
        # TC1
        NEW_ORGANIZER = 'other@gmail.com'
        
        event.create_on_behalf(mock_api, NEW_ORGANIZER)
        
        # api call
        self.assertEqual(mock_api.events().move().execute.call_count, 1)
        
        # called used same organizer (email)
        executed = mock_api.events.return_value.move.call_args_list[0]
        self.assertEqual(executed[1]['destination'], NEW_ORGANIZER)
        
        # invalid inputs
        # TC2 (missing inputs)
        with self.assertRaises(Exception):
            event.create_on_behalf(mock_api)
            
        # TC3
        with self.assertRaises(ValueError):
            event.create_on_behalf(mock_api, "other @gmail.com")
            
    def test_change_organizer(self):
        """ Tests change_organizer. Tests if an organizer of an event is successfully changed. """
        # mock api
        mock_api = MagicMock()

        # create event 
        attendees = [Attendees("John","jsmith@gmail.com")]
        event = Calendar("An event", "Official Meeting",'10-OCT-2022','08:00','10-OCT-2022','08:00', 
                      "123 Fake Street Clayton VIC 3400", "confirmed", attendees)
        
        # valid inputs
        # TC1
        NEW_OWNER = "newowner@gmail.com"
        EVENT_ID = "jabsdr03t8fb3ph1aet2hsilro"
        
        # test api call
        event.change_organizer(mock_api, EVENT_ID, NEW_OWNER)
        self.assertEqual(mock_api.events().move().execute.call_count, 1)
        
        # api called with correct organizer
        executed = mock_api.events.return_value.move.call_args_list[0]
        self.assertEqual(executed[1]['destination'], NEW_OWNER)
        
        # TC2 (program does not raise exception if same owner)
        NEW_OWNER = "jsmith@gmail.com"
        event.change_organizer(mock_api, EVENT_ID, NEW_OWNER)
        self.assertEqual(mock_api.events().move().execute.call_count, 2)
        
        # invalid inputs
        # TC3
        NEW_OWNER = "newowner @gmail.com"
        EVENT_ID = "jabsdr03t8fb3ph1aet2hsilro"
        
        with self.assertRaises(ValueError):
            event.change_organizer(mock_api, EVENT_ID, NEW_OWNER)
            
        # TC4
        NEW_OWNER = "newowner@gmail.com"
        EVENT_ID = "jabsdr03t8f b3ph1aet2hsilr"
        
        with self.assertRaises(ValueError):
            event.change_organizer(mock_api, EVENT_ID, NEW_OWNER)
            
        # TC5
        NEW_OWNER = "newowner@ gmail.com"
        EVENT_ID = "jabsdr03t8f b3ph1aet2hsilr"
        
        with self.assertRaises(ValueError):
            event.change_organizer(mock_api, EVENT_ID, NEW_OWNER)
        
        # missing inputs   
        # TC6
        EVENT_ID = "jabsdr03t8fab3ph1aet2hsilr"
        
        with self.assertRaises(Exception):
            event.change_organizer(mock_api, EVENT_ID)
            
        # TC7
        NEW_OWNER = "newowner@gmail.com"
        
        with self.assertRaises(Exception):
            event.change_organizer(mock_api, NEW_OWNER)
            
    def test_update_event_title(self):
        """ Tests update_event_title. Tests if the title of an event was succesfully changed. """
        # mock api
        mock_api = MagicMock()
        # real event
        attendees = []
        realEvent = Calendar("A real event",'Official Meeting','10-OCT-2022','08:00','10-OCT-2022','08:00',
                          '123 Fake Street Clayton VIC 3400','confirmed',attendees)
        
        # valid input
        # TC1
        EVENT_ID = "jabsdr03t8fb3ph1aet2hsilro"
        NEW_TITLE = "Another title"
        
        realEvent.update_event_title(mock_api, EVENT_ID, NEW_TITLE)
        
        patch_call = mock_api.events.return_value.patch.call_args_list[0]
        
        # patched with title provided
        self.assertEqual(patch_call[1]['body']['summary'], NEW_TITLE)
        
        # patched with id provided
        self.assertEqual(patch_call[1]['eventId'], EVENT_ID)
        
        # send notifications
        self.assertEqual(patch_call[1]['sendUpdates'], "all")
        
        # invalid inputs 
        # TC2
        EVENT_ID = "tooshort"
        NEW_TITLE = "Another title"
        
        with self.assertRaises(ValueError):
            realEvent.update_event_title(mock_api, EVENT_ID, NEW_TITLE)
        
        # missing inputs
        EVENT_ID = "jabsdr03t8fb3ph1aet2hsilro"
        NEW_TITLE = "IM GOING MAD - Carson"
        
        # TC3
        with self.assertRaises(Exception):
            realEvent.update_event_title(mock_api, EVENT_ID)
            
        # TC4
        with self.assertRaises(Exception):
            realEvent.update_event_title(mock_api, NEW_TITLE)
            
    def test_update_event_dates(self):
        """ Tests update_event_dates. Updates the start and end dates for events. """
        # mock api
        mock_api = MagicMock()
        # real event
        attendees = []
        realEvent = Calendar("A real event",'Official Meeting','10-OCT-2022','08:00','10-OCT-2022','08:00',
                          '123 Fake Street Clayton VIC 3400','confirmed',attendees)
        
        # valid inputs
        EVENT_ID = "jabsdr03t8fb3ph1aet2hsilro"
        NEW_START = "2020-08-03"
        NEW_END = "2021-08-03"
        
        realEvent.update_event_dates(mock_api, EVENT_ID, NEW_START, NEW_END)
        
        # assert api call
        mock_api.events().patch().execute.assert_called_once()
        
        patch_call = mock_api.events.return_value.patch.call_args_list[0]

        # assert notifications sent
        self.assertEqual(patch_call[1]['sendUpdates'], "all")
        
        # TC1
        # assert dates passed during api call are correct
        self.assertEqual(patch_call[1]['body']['start']['date'], NEW_START)
        self.assertEqual(patch_call[1]['body']['end']['date'], NEW_END)
        
        # invalid inputs
        # NOTE: update_event_dates is implemented slightly differently from other methods \
            # validateEventDates returns False instead of raising a ValueError immediately, \
            # so, to test this, we assert that the api is not called again if validateEventDates is false.
        # TC2
        EVENT_ID = "tooshort"
        NEW_START = "2020-08-03"
        NEW_END = "2021-08-03"
        
        with self.assertRaises(ValueError):
            realEvent.update_event_dates(mock_api, EVENT_ID, NEW_START, NEW_END)
        
        # TC3
        EVENT_ID = "jabsdr03t8fb3ph1aet2hsilro"
        NEW_START = "2020-08-03222"
        NEW_END = "2021-08-03"
        
        self.assertTrue(mock_api.events().patch().execute.call_count, 1)
        
        # TC4
        EVENT_ID = "jabsdr03t8fb3ph1aet2hsilro"
        NEW_START = "2020-08-03"
        NEW_END = "2021-08-03222"
        
        self.assertTrue(mock_api.events().patch().execute.call_count, 1)
        
        # TC5 start date later than end date (if newStart > newEnd:)
        EVENT_ID = "jabsdr03t8fb3ph1aet2hsilro"
        NEW_START = "2021-08-03"
        NEW_END = "2020-08-03"
        
        with self.assertRaises(Exception):
            realEvent.update_event_dates(mock_api, EVENT_ID, NEW_START, NEW_END)
        
        # missing inputs
        EVENT_ID = "jabsdr03t8fb3ph1aet2hsilro"
        NEW_START = "2020-08-03"
        NEW_END = "2021-08-03"
        
        # TC6
        with self.assertRaises(Exception):
            realEvent.update_event_dates(mock_api, EVENT_ID, NEW_START)
        
        # TC7
        with self.assertRaises(Exception):
            realEvent.update_event_dates(mock_api, EVENT_ID, NEW_END)
            
        # TC8
        with self.assertRaises(Exception):
            realEvent.update_event_dates(mock_api, NEW_START, NEW_END)  
             
    def test_get_attendees(self):
        """ Tests get_attendees. Returns a specific number of attendees of an event as a list. """
        
        EVENT_ID = "jabsdr03t8fb3ph1aet2hsilro"
        
        # mock api
        mock_api = MagicMock()
        # mock event
        mock_event = MagicMock()
        
        # TC1
        COUNT = -1
        with self.assertRaises(ValueError):
            attendees = Calendar.get_attendees(mock_event, mock_api, EVENT_ID, COUNT)
          
        # TC2
        COUNT = 0
        attendees = Calendar.get_attendees(mock_event, mock_api, EVENT_ID, COUNT)
        
        # api call
        self.assertEqual(
            mock_api.events().get().execute.call_count, 1)
        
        # called using ID provided
        executed = mock_api.events.return_value.get.call_args_list[0]
        self.assertEqual(executed[1]['eventId'], EVENT_ID)
        
        # attendee list of same length returned (as specified as count input parameter)
        self.assertEqual(len(attendees), COUNT)
        
        # TC3
        COUNT = 1
        attendees = Calendar.get_attendees(mock_event, mock_api, EVENT_ID, COUNT)
        
        self.assertEqual(len(attendees), COUNT)
          
        # TC4
        COUNT = 19
        attendees = Calendar.get_attendees(mock_event, mock_api, EVENT_ID, COUNT)
        
        self.assertEqual(len(attendees), COUNT)
        
        # TC5
        COUNT = 20
        attendees = Calendar.get_attendees(mock_event, mock_api, EVENT_ID, COUNT)
        self.assertEqual(len(attendees), COUNT)
        
        # TC6
        COUNT = 21
        with self.assertRaises(ValueError):
            attendees = Calendar.get_attendees(mock_event, mock_api, EVENT_ID, COUNT)
            
        # invalid ID
        # TC7
        COUNT = 19
        EVENT_ID = "tooshort"
        
        with self.assertRaises(ValueError):
            attendees = Calendar.get_attendees(mock_event, mock_api, EVENT_ID, COUNT)
        
        # missing inputs
        # TC8
        COUNT = 19
        with self.assertRaises(Exception):
            attendees = Calendar.get_attendees(mock_event, mock_api, EVENT_ID)
            
        # TC9
        with self.assertRaises(Exception):
            attendees = Calendar.get_attendees(mock_event, mock_api, COUNT)
        
    def test_add_attendee(self):
        """ Tests add_attendee. Tests if an attendee is added to the event """
        # mock api
        mock_api = MagicMock()
        # real event
        attendees = []
        realEvent = Calendar("A real event",'Official Meeting','10-OCT-2022','08:00','10-OCT-2022','08:00',
                          '123 Fake Street Clayton VIC 3400','confirmed',attendees)
        
        # valid input
        EVENT_ID = "jabsdr03t8fb3ph1aet2hsilro"
        ATTENDEE_NAME = "John Smith"
        ATTENDEE_EMAIL = "me@gmail.com"
        event = realEvent.add_attendee(mock_api, EVENT_ID, ATTENDEE_EMAIL, ATTENDEE_NAME)
        
        # assert api calls
        self.assertEqual(
            mock_api.events().get().execute.call_count, 1)
        
        self.assertEqual(
            mock_api.events().patch().execute.call_count, 1)
        
        # assert api called with provided id
        get_call = mock_api.events.return_value.get.call_args_list[0]
        self.assertEqual(get_call[1]['eventId'], EVENT_ID)
        
        # assert if notifications sent
        get_patch = mock_api.events.return_value.patch.call_args_list[0]
        self.assertEqual(get_patch[1]['sendUpdates'], "all")
        
        # assert api called with inputs provided
        # TC1
        self.assertEqual(get_patch[1]['body']['attendees'][0]['email'], ATTENDEE_EMAIL)
        self.assertEqual(get_patch[1]['body']['attendees'][0]['displayName'], ATTENDEE_NAME)
        
        # invalid inputs
        # TC2
        ATTENDEE_EMAIL = "you gmail com"
        
        with self.assertRaises(ValueError):
            realEvent.add_attendee(mock_api, EVENT_ID, ATTENDEE_EMAIL, ATTENDEE_NAME)
            
        # invalid inputs
        # TC3
        EVENT_ID = "waytoolongwaytoolongwaytoolongwaytoolongwaytoolong"
        ATTENDEE_NAME = "John Smith"
        ATTENDEE_EMAIL = "me@gmail.com"
        
        with self.assertRaises(ValueError):
            realEvent.add_attendee(mock_api, EVENT_ID, ATTENDEE_EMAIL, ATTENDEE_NAME)
        
        # anything after exception raised should not be called
        self.assertEqual(
            mock_api.events().get().execute.call_count, 1)
        
        self.assertEqual(
            mock_api.events().patch().execute.call_count, 1)
        
        # missing inputs
        # TC4
        with self.assertRaises(Exception):
            realEvent.add_attendee(mock_api, EVENT_ID, ATTENDEE_EMAIL)
            
        # TC5
        with self.assertRaises(Exception):
            realEvent.add_attendee(mock_api, EVENT_ID, ATTENDEE_NAME)
            
        # TC6
        with self.assertRaises(Exception):
            realEvent.add_attendee(mock_api, ATTENDEE_EMAIL, ATTENDEE_NAME)
        
    def test_delete_attendee(self):
        """ Tests delete_attendee. Tests if an attendee is deleted from an event. """
        # mock api
        mock_api = MagicMock()
        # real event
        attendees = [Attendees("Me", "me@gmail.com", "It's me")]
        realEvent = Calendar("A real event",'Official Meeting','10-OCT-2022','08:00','10-OCT-2022','08:00',
                          '123 Fake Street Clayton VIC 3400','confirmed',attendees)
        
        # valid input
        # TC1
        EVENT_ID = "jabsdr03t8fb3ph1aet2hsilro"
        ATTENDEE_EMAIL = "me@gmail.com"
        event = Calendar.delete_attendee(realEvent, mock_api, EVENT_ID, ATTENDEE_EMAIL)
        
        self.assertEqual(
            mock_api.events().get().execute.call_count, 1)
        
        self.assertEqual(
            mock_api.events().patch().execute.call_count, 1) 
        
        # program does not raise exception if target not found
        EVENT_ID = "jabsdr03t8fb3ph1aet2hsilro"
        ATTENDEE_EMAIL = "notme@gmail.com"
        
        updated = Calendar.delete_attendee(realEvent, mock_api, EVENT_ID, ATTENDEE_EMAIL)
        
        self.assertEqual(
            mock_api.events().get().execute.call_count, 2)
        
        self.assertEqual(
            mock_api.events().patch().execute.call_count, 2)
        
        # assert sending notifications
        patch_call = mock_api.events.return_value.patch.call_args_list[0]
        self.assertEqual(patch_call[1]['sendUpdates'], "all")
        
        # entire function executed
        self.assertEqual(updated, ATTENDEE_EMAIL)
        
        # invalid input
        # TC2
        EVENT_ID = "jabsdr03t8fb3ph1aet2hsilro"
        ATTENDEE_EMAIL = "me gmail com"
        
        with self.assertRaises(ValueError):
            event = Calendar.delete_attendee(realEvent, mock_api, EVENT_ID, ATTENDEE_EMAIL)
        
        # TC3
        EVENT_ID = "tooshort"
        ATTENDEE_EMAIL = "me@gmail.com"
        
        # TC4
        with self.assertRaises(ValueError):
            event = Calendar.delete_attendee(realEvent, mock_api, EVENT_ID, ATTENDEE_EMAIL)
            
        # missing inputs
        EVENT_ID = "tooshort"
        ATTENDEE_EMAIL = "me@gmail.com"
        
        # TC5
        with self.assertRaises(Exception):
            event = Calendar.delete_attendee(realEvent, mock_api, EVENT_ID)
            
        # TC6
        with self.assertRaises(Exception):
            event = Calendar.delete_attendee(realEvent, mock_api, ATTENDEE_EMAIL)
        
    def test_update_attendee(self):
        """ Tests update_attendee. Tests if an attendee's information is updated in an event. """
        # mock api
        mock_api = MagicMock()
        # real event
        attendees = [Attendees("Rob", "rob@gmail.com", "Hi"), Attendees("Me", "me@gmail.com", "It's me")]
        realEvent = Calendar("A real event",'Official Meeting','10-OCT-2022','08:00','10-OCT-2022','08:00',
                          '123 Fake Street Clayton VIC 3400','confirmed',attendees)
        
        # valid inputs 
        # TC1
        EVENT_ID = "jabsdr03t8fb3ph1aet2hsilro"
        OLD_EMAIL = "rob@gmail.com"
        NEW_EMAIL = "rob2@gmail.com"
        
        updated = realEvent.update_attendee(mock_api, EVENT_ID, OLD_EMAIL, NEW_EMAIL)
        
        self.assertEqual(updated, NEW_EMAIL)
        
        # assert notifications sent
        patch_call = mock_api.events.return_value.patch.call_args_list[0]
        self.assertEqual(patch_call[1]['sendUpdates'], "all")
        
        self.assertEqual(
            mock_api.events().get().execute.call_count, 1)
        
        self.assertEqual(
            mock_api.events().patch().execute.call_count, 1)
        
        # invalid inputs
        # TC2
        EVENT_ID = "jabsdr03t8fb3ph1aet2hsilro"
        OLD_EMAIL = "rob gmail com"
        NEW_EMAIL = "rob2@gmail.com"
        
        with self.assertRaises(ValueError):
           realEvent.update_attendee(mock_api, EVENT_ID, OLD_EMAIL, NEW_EMAIL)
            
        # TC3
        EVENT_ID = "jabsdr03t8fb3ph1aet2hsilro"
        OLD_EMAIL = "rob@gmail.com"
        NEW_EMAIL = "rob2 gmail com"
        
        # TC4
        with self.assertRaises(ValueError):
            realEvent.update_attendee(mock_api, EVENT_ID, OLD_EMAIL, NEW_EMAIL)
            
        EVENT_ID = "tooshort"
        OLD_EMAIL = "rob@gmail.com"
        NEW_EMAIL = "rob2@gmail.com"
        
        # TC5
        with self.assertRaises(ValueError):
            realEvent.update_attendee(mock_api, EVENT_ID, OLD_EMAIL, NEW_EMAIL)
            
        # missing inputs 
        EVENT_ID = "jabsdr03t8fb3ph1aet2hsilro"
        OLD_EMAIL = "rob@gmail.com"
        NEW_EMAIL = "rob2@gmail.com"
        
        # TC6
        with self.assertRaises(Exception):
            realEvent.update_attendee(mock_api, EVENT_ID, OLD_EMAIL)
            
        # TC7
        with self.assertRaises(Exception):
            realEvent.update_attendee(mock_api, EVENT_ID, NEW_EMAIL)
            
        # TC8
        with self.assertRaises(Exception):
            realEvent.update_attendee(mock_api, OLD_EMAIL, NEW_EMAIL)
            
    def test_view_events(self):
        """ Tests view_events. Displays events 5 years ago and 5 years from now. """
        # times (5 years ago, present, and in the future) for testing
        NOW = (datetime.datetime.now().utcnow().isoformat() + 'Z')[:4]
        THEN = str(int(NOW)-5)
        FUTURE = str(int(NOW)+5)
        
        # mock api
        mock_api = MagicMock()
        
        view_events(mock_api)
        
        # api call
        self.assertEqual(
            mock_api.events.return_value.list.return_value.execute.return_value.get.call_count, 1)
        
        # assert times are correct
        list_call = mock_api.events.return_value.list.call_args_list[0]
        
        self.assertEqual(list_call[1]['timeMin'][:4], THEN)
        self.assertEqual(list_call[1]['timeMax'][:4], FUTURE)
        
    def test_respond_invitation(self):
        """ Tests respond_invitation. Tests if an attendee's response status is updated in an event. """
        # mock api
        mock_api = MagicMock()
        # real event
        attendees = [Attendees("Me", "me@gmail.com", "It's me")]
        realEvent = Calendar("A real event",'Official Meeting','10-OCT-2022','08:00','10-OCT-2022','08:00',
                          '123 Fake Street Clayton VIC 3400','confirmed',attendees)
        
        # valid inputs
        # TC1
        EVENT_ID = "jabsdr03t8fb3ph1aet2hsilro"
        EMAIL = "me@gmail.com"
        RESPONSE = "declined"
        
        responded = realEvent.respond_invitation(mock_api, EVENT_ID, EMAIL, RESPONSE)
        
        patch_call = mock_api.events.return_value.patch.call_args_list[0]
        
        # api call
        self.assertEqual(mock_api.events.return_value.patch.call_count, 1)
        
        # notifications sent
        self.assertEqual(patch_call[1]['sendUpdates'], "all")
        
        # entire code is executed
        self.assertEqual(responded, RESPONSE)
        
        # invalid inputs
        # TC2
        EVENT_ID = "tooshort"
        EMAIL = "me@gmail.com"
        RESPONSE = "accepted"
        
        with self.assertRaises(ValueError):
            realEvent.respond_invitation(mock_api, EVENT_ID, EMAIL, RESPONSE)
        
        # TC3
        EVENT_ID = "jabsdr03t8fb3ph1aet2hsilro"
        EMAIL = "me gmail.com"
        RESPONSE = "declined"
        
        with self.assertRaises(ValueError):
            realEvent.respond_invitation(mock_api, EVENT_ID, EMAIL, RESPONSE)
        
        # TC4
        EVENT_ID = "jabsdr03t8fb3ph1aet2hsilro"
        EMAIL = "me@gmail.com"
        RESPONSE = "invalid"
        
        # TC5
        with self.assertRaises(Exception):
            realEvent.respond_invitation(mock_api, EVENT_ID, EMAIL, RESPONSE)
            
        # empty inputs
        EVENT_ID = "tooshort"
        EMAIL = "me@gmail.com"
        RESPONSE = "tentative"
        
        # TC6
        with self.assertRaises(Exception):
            realEvent.respond_invitation(mock_api, EVENT_ID, EMAIL)
            
        # TC7
        with self.assertRaises(Exception):
            realEvent.respond_invitation(mock_api, EVENT_ID, RESPONSE)
            
        # TC8
        with self.assertRaises(Exception):
            realEvent.respond_invitation(mock_api, EMAIL, RESPONSE)
        
    def test_validate_email(self):
        """ Tests if validate_email raises Exceptions when invalid inputs are provided. """        
        # TC1
        EMAIL = "me @gmail.com"
        
        with self.assertRaises (ValueError):
            validate_email(EMAIL)
            
        # TC2
        EMAIL = "me gmail com"
        
        with self.assertRaises (ValueError):
            validate_email(EMAIL)

    def test_validate_event_id(self):
        """ Tests if validate_event_id raises Exceptions when invalid inputs are provided. """ 
        # TC1
        EVENT_ID = "waytoolongwaytoolongwaytoolongwaytoolong"
        
        with self.assertRaises (ValueError):
            validate_email(EVENT_ID)
        
        # TC2
        EVENT_ID = "id h4s n0 sp4ac35"
        
        with self.assertRaises (ValueError):
            validate_email(EVENT_ID)
    
    def test_import_event(self):
        """test if the import_event raises and exception when blank file is provided"""
        file = ""
        file2 = "test.txt"
        mock_api = MagicMock()

        #TC1: Empty Value Provided
        with self.assertRaises(Exception):
            import_Event(mock_api,file)

        #TC2: invalid file extension provided
        with self.assertRaises(Exception):
            import_Event(mock_api,file2)
    
    def test_export_event(self):
        """Test if the export event raises exception when an empty list is provided"""
        empty_list = []
        with self.assertRaises(Exception):
            export_event(empty_list)
        
def main():
    # Create the test suite from the cases above.
    suite = unittest.TestLoader().loadTestsFromTestCase(MyEventManagerTest)
    # This will run the test suite.
    unittest.TextTestRunner(verbosity=2).run(suite)
    
main()

# coverage run --branch unittest MyEventManagerTest.py
# coverage report -m
# coverage html
