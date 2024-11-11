import unittest
from unittest import mock
from datetime import datetime, timedelta
from website.auth import get_google_credentials, fetch_data_from_api
from website.models import convert_to_iso_format, add_minutes_to_time, add_5_30_hrs, Appointment, schedule_event
from datetime import timezone
from website import create_app  
from website.models import db 
from flask import session

app = create_app() 

class TestAuthFunctions(unittest.TestCase):
    
    # @classmethod
    # def setUpClass(cls):
    #     # Set up the app context once for all tests
    #     cls.app = app
    #     cls.app_context = cls.app.app_context()
    #     cls.app_context.push()
    
    # @classmethod
    # def tearDownClass(cls):
    #     # Clean up the app context
    #     cls.app_context.pop()

    # @mock.patch('website.auth.Credentials')
    # @mock.patch('os.path.exists')
    # @mock.patch('website.auth.InstalledAppFlow')
    # def test_get_google_credentials(self, mock_flow, mock_exists, mock_credentials):
    #     with app.test_request_context('/'):
    #         # Mock session with expected credentials structure
    #         session['credentials'] = {
    #             'token': 'test_token',
    #             'refresh_token': 'test_refresh_token',
    #             'token_uri': 'test_token_uri',
    #             'client_id': 'test_client_id',
    #             'client_secret': 'test_client_secret',
    #             'scopes': ['test_scope']
    #         }

    #         # Mock os.path.exists to simulate the presence of 'token.json'
    #         mock_exists.return_value = True
            
    #         # Mock the credentials object with expected properties
    #         mock_creds = mock.Mock()
    #         mock_creds.valid = True
    #         mock_creds.token = 'test_token'
    #         mock_credentials.from_authorized_user_file.return_value = mock_creds
            
    #         # Call the function under test
    #         creds = get_google_credentials()
            
    #         # Assert that the returned credentials are the mocked ones
    #         self.assertIsNotNone(creds, "Expected credentials but got None")

    
    
    @mock.patch('website.auth.requests.get')
    @mock.patch('website.auth.get_google_credentials')
    def test_fetch_data_from_api(self, mock_get_google_credentials, mock_requests_get):
        # Mock the credentials and response
        mock_creds = mock.Mock(token="mock_token")
        mock_get_google_credentials.return_value = mock_creds
        mock_response = mock.Mock()
        mock_response.json.return_value = {"data": "test"}
        mock_requests_get.return_value = mock_response
        
        response = fetch_data_from_api()
        self.assertEqual(response, {"data": "test"})

class TestModelFunctions(unittest.TestCase): 

    def test_convert_to_iso_format1(self):
        date_str = "01/01/23"
        time_str = "15:00"
        result = convert_to_iso_format(date_str, time_str)
        expected = datetime(2023, 1, 1, 15, 0).replace(tzinfo=timezone(timedelta(hours=5, minutes=30))).isoformat()
        self.assertEqual(result, expected)

    def test_convert_to_iso_format2(self):
        date_str = "15/10/24"
        time_str = "17:30"
        result = convert_to_iso_format(date_str, time_str)
        expected = datetime(2024, 10, 15, 17, 30).replace(tzinfo=timezone(timedelta(hours=5, minutes=30))).isoformat()
        self.assertEqual(result, expected)

    def test_convert_to_iso_format3(self):
        date_str = "18/07/21"
        time_str = "06:23"
        result = convert_to_iso_format(date_str, time_str)
        expected = datetime(2021, 7, 18, 6, 23).replace(tzinfo=timezone(timedelta(hours=5, minutes=30))).isoformat()
        self.assertEqual(result, expected)
    
    def test_convert_to_iso_format4(self):
        date_str = "28/04/25"
        time_str = "00:00"
        result = convert_to_iso_format(date_str, time_str)
        expected = datetime(2025, 4, 28, 0, 0).replace(tzinfo=timezone(timedelta(hours=5, minutes=30))).isoformat()
        self.assertEqual(result, expected)
    

    def test_add_minutes_to_time1(self):
        time_str = "14:00"
        result = add_minutes_to_time(time_str, 30)
        self.assertEqual(result, "14:30")
    
    def test_add_minutes_to_time2(self):
        time_str = "23:30"
        result = add_minutes_to_time(time_str, 30)
        self.assertEqual(result, "00:00")
    
    def test_add_minutes_to_time3(self):
        time_str = "23:30"
        result = add_minutes_to_time(time_str, 45)
        self.assertEqual(result, "00:15")
    
    def test_add_minutes_to_time4(self):
        time_str = "11:00"
        result = add_minutes_to_time(time_str, 70)
        self.assertEqual(result, "12:10")

    def test_add_5_30_hrs1(self):
        time_str = "09:00"
        result = add_5_30_hrs(time_str)
        self.assertEqual(result, "14:30")

    def test_add_5_30_hrs2(self):
        time_str = "23:00"
        result = add_5_30_hrs(time_str)
        self.assertEqual(result, "04:30")
    
    def test_add_5_30_hrs3(self):
        time_str = "18:30"
        result = add_5_30_hrs(time_str)
        self.assertEqual(result, "00:00")
    
    def test_add_5_30_hrs4(self):
        time_str = "16:45"
        result = add_5_30_hrs(time_str)
        self.assertEqual(result, "22:15")

    @mock.patch('website.models.get_calendar_service')
    def test_schedule_event1(self, mock_get_calendar_service):
        # Mock the calendar service and event creation
        mock_service = mock.Mock()
        mock_get_calendar_service.return_value = mock_service
        mock_event = {"id": "test_event1"}
        mock_service.events().insert().execute.return_value = mock_event
        
        result = schedule_event("Test Event", "2023-01-01T09:00:00+05:30", "2023-01-01T10:00:00+05:30")
        self.assertEqual(result, mock_event)
    
    @mock.patch('website.models.get_calendar_service')
    def test_schedule_event2(self, mock_get_calendar_service):
        # Mock the calendar service and event creation
        mock_service = mock.Mock()
        mock_get_calendar_service.return_value = mock_service
        mock_event = {"id": "test_event2"}
        mock_service.events().insert().execute.return_value = mock_event
        
        result = schedule_event("Test Event", "2024-08-15T23:40:00+05:30", "2024-08-15T00:10:00+05:30")
        self.assertEqual(result, mock_event)
    
    @mock.patch('website.models.get_calendar_service')
    def test_schedule_event3(self, mock_get_calendar_service):
        # Mock the calendar service and event creation
        mock_service = mock.Mock()
        mock_get_calendar_service.return_value = mock_service
        mock_event = {"id": "test_event3"}
        mock_service.events().insert().execute.return_value = mock_event
        
        result = schedule_event("Test Event", "2022-12-31T23:40:00+05:30", "2023-01-01T00:10:00+05:30")
        self.assertEqual(result, mock_event)
    
    @mock.patch('website.models.get_calendar_service')
    def test_schedule_event4(self, mock_get_calendar_service):
        # Mock the calendar service and event creation
        mock_service = mock.Mock()
        mock_get_calendar_service.return_value = mock_service
        mock_event = {"id": "test_event4"}
        mock_service.events().insert().execute.return_value = mock_event
        
        result = schedule_event("Test Event", "2023-11-12T09:15:00+05:30", "2023-11-12T10:00:00+05:30")
        self.assertEqual(result, mock_event)
    
    # @mock.patch('website.models.db')
    # def test_appointment_unbooked_check_availability1(self, mock_db):
    # # Create and push an application context
    #     with app.app_context():
    #         # Mock the database query response
    #         mock_db.query.filter_by.return_value.all.return_value = []
            
    #         day = "Mon"
    #         time = "09:00"
            
    #         # Call the function within the app context
    #         result = Appointment.checkAvailability(day, time)
    #         self.assertEqual(result, [])
    
    # @mock.patch('website.models.db')
    # def test_appointment_unbooked_check_availability2(self, mock_db):
    # # Create and push an application context
    #     with app.app_context():
    #         # Mock the database query response
    #         mock_db.query.filter_by.return_value.all.return_value = []
            
    #         day = "Mon"
    #         time = "10:10"
            
    #         # Call the function within the app context
    #         result = Appointment.checkAvailability(day, time)

    #         self.assertEqual(len(result),0)
    
    # @mock.patch('website.models.db')
    # def test_appointment_unbooked_check_availability3(self, mock_db):
    # # Create and push an application context
    #     with app.app_context():
    #         # Mock the database query response
    #         mock_db.query.filter_by.return_value.all.return_value = []
            
    #         day = "Wed"
    #         time = "19:10"
            
    #         # Call the function within the app context
    #         result = Appointment.checkAvailability(day, time)

    #         self.assertEqual(len(result),0)

    # @mock.patch('website.models.db')
    # def test_appointment_unbooked_check_availability4(self, mock_db):
    # # Create and push an application context
    #     with app.app_context():
    #         # Mock the database query response
    #         mock_db.query.filter_by.return_value.all.return_value = []
            
    #         day = "Fri"
    #         time = "11:00"
            
    #         # Call the function within the app context
    #         result = Appointment.checkAvailability(day, time)

    #         self.assertNotEqual(len(result),0)
# Run the tests with python -m unittest discover -s tests -p "test_*.py"
