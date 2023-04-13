# Test Cases Documentation and Rationale

## Additional Assertions
Throughout our test cases, we have included some additional assertions that do not utilise a specific test strategy. The purpose of their inclusion is more specifically explained with in-line comments. They will be briefly explained here to prevent writing the same block of text repeatedly. The team often performed these assertions together with one or two of the test cases.

Some of these assertions include:

1. self.assertEqual(mock_api.events().{ACTION}.execute.call_count, {INTEGER}):
This was mainly used when we had to make sure that the API was being called correctly. For example, it shouldn't be called if an exception was previously raised.

2. mock_api.events.return_value.move.call_args_list[0]
This was used when we had to assert that the correct inputs or parameters were being provided when we were executing a change using the API. This is usually followed by one or more assertion statement(s). For example, this was used when we had to verify that notifications were being sent after code execution.

3. mock_api.events().patch().execute.assert_called_once()
This was another method used when we had to assert that the mock API was called once. 


## Input Validation
These are functions that validate common inputs. 
  
1. def validate_email(email)  

Strategy: Decision/Condition Coverage

This function raises a ValueError if an invalid email is provided. For an email to be invalid, it is either missing an "@" or has whitespaces in it. Using Decision/Condition Coverage evaluates both these conditions individually at least once. And the test cases here only test if the "if" statement is executed, when invalid inpupts are provided. Cases where the "if" statement is not executed (i.e. a valid email is provided), is omitted here as it is already tested when a function calls this method. For example, add_attendee() uses this method and evaluates the case where "if" is not executed. Collectively, these cover all statements and branches of email validation.

Decision/Condition Coverage was chosen instead of Equivalence Class partitioning to evaluate the conditions individually. This was to ensure that either of these conditions would be recognised by the program as invalid. EC may have 1 less test case, but it does not consider both the TRUE/FALSE state of both conditionals.

2. def validate_event_id(eventId):

Strategy: Decision/Condition Coverage

The reasoning for using this test strategy, and the justification for its test cases, are similar to validate_email().

3. def test_validate_date_format(self):  

Strategy: Equivalence Class Partitioning  

This function raises a ValueError if the date format provided does not satisfy the format of YYYY-mm-dd or dd-Mon-YYYY as specified in the requirements.  
EC1: format of YYYY-mm-dd  
EC2: format of dd-Mon-YYYY  
EC3: Other Strings that are not in either format of dd-Mon-YYYY or YYYY-mm-dd  
EC4: empty input  

EC5: returns  
EC6: raises ValueError

This test strategy test for all possible input of strings/date value and it covers all statements and branches for validateDateFormat function and return the validation of the date string provided.

4. def test_valid_eventType(self):
Strategy: Equivalence Class Partitioning  
This function raises a ValueError if the event type provided are not one of the three options which is:
"Physical Event", "Online Meeting", "Official Meeting", which creates the following ECs:

EC1: Physical Event  
EC2: Online Meeting  
EC3: Official Meeting  
EC4: Other inputs  

EC5: Returns  
EC6: Raises ValueError

This test strategy test for all possible input of eventType and it covers all the statements and branches for validateEventType functin and return the validation of eventType provided.

3. def test_address_validation(self):

Strategy: Decision/Condition Coverage  

This function raises a ValueError if an invalid address is provided. For an address to be invalid, it must be missing one or more of the following: Unit number, Street, City, State, Zip Code. Using Decision/Condition Coverage evaluates if one of these requirements are missing. If it fulfills all the criteria, the function will return true, else the function will return false and raises ValueError. Hence, it covers all the branch and statement in validateAddressFormat.

4. def test_max_attendees(self):

Strategy: Decision/Condition Coverage

This function Raises an Exception if more than 20attendees are added into the event. It checks for the length of the list containing the attendees. If it exceeds 20 then it returns an exception telling the user that numbers of attendees must not exceed 20. This covers all the branch and statements for attendeesValidation.

## Program Methods
# NOTE: the functions being tested are written after "test_" in the tests below. So, test_create_on_behalf are the test created for create_on_behalf in the main applicaiton.

1. def test_get_upcoming_events_number(self):

Strategy: Equivalence Class Partioning, Boundary Value Analysis

The get_upcoming_events() method provided does validation for the number_of_events input. This can either be valid or invaid which creates the following ECs:

EC1: number_of_events > 0  
EC2: number_of_events <= 0  

EC3: returns  
EC4: raises ValueError

The test strategy test the on-point and its surrounding off-points and 1 and -1. These test cases also conviniently covers all branches and paths in the function, so branch coverage is fully tested as well.

2. def test_create_on_behalf(self):

Strategy: Equivalence Class Partioning

As email validation is already tested in test_validate_email, the possible ways in which email can be invalid is omitted in the test cases for create_on_behalf(), only valid inputs and one invalid input will be tested. This will be a recurring strategy/pattern for the remaining test cases if they have event ID or email as their inputs.

EC1: newOrganizer (email) is valid  
EC2: newOrganizer is invalid  
EC3: newOrganizer is empty  

EC4: organizer changed  
EC5: raises Exception  
EC6: raises ValueError

Similar to 1. def test_get_upcoming_events_number(self), EC also covers all branches and paths in the function. There is only one "if" statement. 

3. def test_change_organizer(self):

Strategy: Category Partitioning, Decision/Condition Coverage

Decision/Condition Coverage was chosen to evaluate the if statement. Since the if statement compares two conditions using an OR operator. Each condition is evaluated to TRUE and FALSE at least once. The test cases also evalute the decision to TRUE (raises Exception) or FALSE. Although Branch Coverage would have technically been sufficient, the team felt that it was a safer option to test the conditions individually, just in case one of the conditionals were not behaving as expected. 

Category Partitioning is used here to test how the different inputs (email and ID) may interact, as each of them may either be valid, invalid or empty, which forms the choices of each category. This interaction, and hence Category Partitioning is only tested once in this program, as we would get a lot of overlapping test cases if were to do this for every function. 

Similar to previous tests, all possibilites of invalid instances of email and ID are only tested once, as they were previously tested.

Categories (Choices): Email (valid, invalid, empty), Event ID (valid, invalid, empty))

Test frames:  
Email      / ID  
####################  
-> valid   / valid  
-> valid   / invalid  
-> invalid / invalid   
-> invalid / valid  
-> empty   / --  
#####################

4. def test_update_event_title(self):

Strategy: Equivalence Class Partioning, Decision/Condition Coverage

The test cases utilise a similar strategy as explained in 3. def test_change_organizer(self), but instead of Category Partioning, EC is used, so invalid inputs are only tested once here. The parameter newTitle is always assumed to be always valid, since users can name the event to their liking.

EC1: eventId is valid  
EC2: eventId is invalid  
EC4: eventId is empty  
EC5: newTitle is empty  

EC6: title changed  
EC7: raises Exception  
EC8: raises ValueError  

There is one "if" statement. All branches are covered.

5. def test_update_event_dates(self):

Strategy: Equivalence Class Partioning, Decision/Condition Coverage

There are three "if" statements here that will be tested using Decision/Condition Coverage, as it is important to test how each of these conditionals affect the decision individually, as any condition that does not behave as expected (raising an Exception when it shouldn't etc.) may potentially break the code.

a. if (eventId is None) or (newStart is None) or (newEnd is None)
b. if newStart > newEnd
c. if (validateDateFormat(newStart)) and (validateDateFormat(newEnd))

The ECs are:

EC1: eventId, newStart and newEnd is valid (TC1)  
EC2: newStart < newEnd (TC1)  
EC3: newStart > newEnd (TC5)  
EC4: eventId is invalid (TC2)  
EC5: newStart is invalid (TC3)  
EC6: newEnd is invalid (TC4)  
EC7: eventId is empty (TC8)   
EC8: newStart is empty (TC7)  
EC9: newEnd is empty (TC6)  

EC10: dates changed (TC1)  
EC11: raises Exception (TC5)  
EC12: raises ValueError (TC2)  

All 12 ECs are covered at least once using 8 test cases (overlaps are not written down). 

TC6 - TC8 covers Decision/Condition Coverage for if (eventId is None) or (newStart is None) or (newEnd is None).
TC1 and TC5 covers Decision/Condition Coverage for if newStart > newEnd.
TC1, TC3 and TC4 covers Decision/Condition Coverage for if (validateDateFormat(newStart)) and (validateDateFormat(newEnd)).

6. def test_get_attendees(self):

Strategy: Equivalence Class Partioning, Boundary Value Analysis, Decision/Condition Coverage

Decision/Condition Coverage tests each conditional in "if (eventId is None) or (count is None)", and the decision to TRUE and FALSE at least once.

Boundary Value Analysis is used here as "count", an integer, is validated within the function. The on-points here are 0 and 20, since there cannot be less than 0 attendees for an event and only up to 20 attendees are supported by the application. Event ID is evaluated as valid and invalid once as usual.

EC1: 0 <= count <= 20  
EC2: count = 0, count = 20 (split into 2 test cases to test the on-points)  
EC3: count < 0, count > 20 (split into 4 test cases to test the off-points, partially overlaps with EC1)  
EC4: count is empty  
EC5: eventId is invalid  
EC6: eventId is empty  

EC7: returns attendee list  
EC8: raise Exception  
EC9: raise ValueError  

7. def test_add_attendee(self):

Strategy: Equivalence Class Partioning, Decision/Condition Coverage

Decision/Condition Coverage tests each conditional in "if (eventId is None) or (attendeeEmail is None) or (attendeeName is None)", and the decision to TRUE and FALSE at least once. Event ID and Email are evaluated as valid and invalid once as usual. EC is used to test each input, outcome and errors individually like the previous tests.

EC1: eventId and attendeeEmail is valid  
EC2: eventId is invalid  
EC3: attendeeEmail is invalid  
EC4: eventId is empty  
EC5: attendeeEmail is empty  
EC6: attendeeName is empty  

EC7: adds attendee to event  
EC8: raise Exception  
EC9: raise ValueError  

8. def test_delete_attendee(self):

Strategy: Equivalence Class Partioning, Decision/Condition Coverage

Rationale is the same as test_add_attendee(self).

EC1: eventId and attendeeEmail is valid    
EC2: eventId is invalid  
EC3: attendeeEmail is invalid  
EC4: eventId is empty  
EC5: attendeeEmail is empty  

EC6: removes attendee from event  
EC7: raise Exception  
EC8: raise ValueError  

9. def test_update_attendee(self):

Strategy: Equivalence Class Partioning, Decision/Condition Coverage

Rationale is the same as test_add_attendee(self).

EC1: eventId, oldAttendeeEmail and newAttendeeEmail is valid  
EC2: eventId is invalid  
EC3: oldAttendeeEmail is invalid  
EC4: newAttendeeEmail is invalid  
EC5: eventId is empty  
EC6: oldAttendeeEmail is empty  
EC7: newAttendeeEmail is empty  

EC8: updates attendee information  
EC9: raise Exception  
EC10: raise ValueError  

10. def test_view_events(self):

Strategy: -

There are no user inputs to this function. However, some assertion was done in the tests to ensure that the API was called using the correct dates. The dates are automatically generated by the program.

11. test_respond_invitation(self):

Strategy: Equivalence Class Partioning, Decision/Condition Coverage

Decision/Condition Coverage evaluates the two "if" statements in the function. So eventId, email, response and the decision is evaluated to TRUE or FALSE at least once. Similarly, each of the conditionals in "if (response != "declined") and (response != "tentative") and (response != "accepted")", and the decision are evaluated to TRUE and FALSE at least once. 

This combination also simultaneously tests all the paths of the function without any extra test cases for path coverage:

start > if > Exception  
start > if > else > if > Exception  
start > if > else > if > ValueError  
start > if > else > if > else > no ValueError > ValueError  
start > if > else > if > else > no ValueError > no ValueError > end  

NOTE: within the email and ID validation functions above, either of these paths may be taken:  
start (from function) > if > ValueError  
start (from function) > if > else > end (no ValueError, back to function)  

The Equivalence Classes are:

EC1: eventId, email and response is valid  
EC2: eventId is invalid  
EC3: email is invalid  
EC4: response is invalid  
EC5: eventId is empty  
EC6: email is empty  
EC7: response is empty  

EC8: response to invitation is updated  
EC9: raise Exception  
EC10: raise ValueError  

12. test_import_event(self):

Strategy: Equivalence Class partitioning  

This function raises a ValueError if the provided file is not a exported json file that contains a list of events, which creates the following ECs:

EC1: Provided file field is empty  
EC2: Provided file have unsupported file extension such as: .txt or .pdf  
EC3: Provided file have empty records  

EC4: Raise Exception
EC5: returns

13. test_export_events(self):

Strategy: Equivalence Class partitioning

This function raises a ValueError if the provided input is empty, which creates the following ECs:  

EC1: Provided list is empty  
EC2: Provided list contains valid records of events list  

EC3: returns  
EC4: Raise Exception



