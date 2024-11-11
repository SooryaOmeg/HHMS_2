from flask import render_template
from .models import Appointment
import os
from dotenv import load_dotenv
import requests
from flask import Blueprint, redirect, url_for, session, request
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import google.auth.transport.requests

load_dotenv()

auth = Blueprint('auth', __name__)

# flow = Flow.from_client_secrets_file('./credentials.json',
#     scopes=['https://www.googleapis.com/auth/calendar'],
#     redirect_uri='http://localhost:5000/auth/callback'
# )
# CLIENT_SECRET_FILE = './credentials.json'
# SCOPES = ['https://www.googleapis.com/auth/calendar']

SCOPES = ['https://www.googleapis.com/auth/calendar']
REDIRECT_URI = os.getenv('REDIRECT_URI', 'http://localhost:5000/auth/callback')

def get_client_config():
    """Creates a client configuration dictionary from environment variables"""
    client_id = os.getenv('GOOGLE_CLIENT_ID')
    client_secret = os.getenv('GOOGLE_CLIENT_SECRET')

    if not client_id or not client_secret:
        raise ValueError("Missing GOOGLE_CLIENT_ID or GOOGLE_CLIENT_SECRET in environment variables")

    return {
        "web": {
            "client_id": os.getenv('GOOGLE_CLIENT_ID'),
            "project_id": os.getenv('GOOGLE_PROJECT_ID'),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_secret": os.getenv('GOOGLE_CLIENT_SECRET'),
            "redirect_uris": [os.getenv('REDIRECT_URI', 'http://localhost:5000/auth/callback')]
        }
    }


def create_flow():
    """Creates a Flow object using environment variables"""
    # client_config = get_client_config()
    # return Flow.from_client_config(
    #     client_config,
    #     scopes=['https://www.googleapis.com/auth/calendar'],
    #     redirect_uri=os.getenv('REDIRECT_URI', 'http://localhost:5000/auth/callback')
    # )
    try:
        client_config = get_client_config()
        flow = Flow.from_client_config(
            client_config,
            scopes=SCOPES,
            redirect_uri=REDIRECT_URI
        )
        return flow
    except Exception as e:
        print(f"Error creating flow: {e}")
        raise

#
# def get_google_credentials():
#     creds = None
#     token_path = 'token.json'  # Where the access and refresh tokens will be stored
#     # Load existing credentials if they are available
#     if os.path.exists(token_path):
#         creds = Credentials.from_authorized_user_file(token_path, SCOPES)
#     # If there are no valid credentials, use the OAuth flow to fetch them
#     if not creds or not creds.valid:
#         if creds and creds.expired and creds.refresh_token:
#             creds.refresh(Request())  # Refresh the token if it's expired
#         else:
#             flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
#             creds = flow.run_local_server(port=0)
#         # Save the credentials for the next run
#         with open(token_path, 'w') as token:
#             token.write(creds.to_json())
#     return creds

def get_google_credentials():
    """Get credentials from session or token file"""
    # First try to get credentials from session
    if 'credentials' in session:
        creds_data = session['credentials']
        creds = Credentials(
            token=creds_data['token'],
            refresh_token=creds_data['refresh_token'],
            token_uri=creds_data['token_uri'],
            client_id=creds_data['client_id'],
            client_secret=creds_data['client_secret'],
            scopes=creds_data['scopes']
        )

        # Refresh token if expired
        if not creds.valid:
            if creds.expired and creds.refresh_token:
                creds.refresh(Request())
                # Update session with new token
                session['credentials']['token'] = creds.token
        return creds

    # If no credentials in session, try token file
    token_path = 'token.json'
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        if creds and creds.valid:
            return creds
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            return creds

    # If no valid credentials found, return None
    return None

def fetch_data_from_api():
    creds = get_google_credentials()
    if not creds:
        return redirect(url_for('auth.login'))
    headers = {
        'Authorization': f'Bearer {creds.token}',
        'Content-Type': 'application/json'
    }
    response = requests.get('https://api.example.com/data', headers=headers)
    response.raise_for_status()
    return response.json()


@auth.route('/login')
def login():
    """Initiate the OAuth2 authorization flow"""
    flow = create_flow()
    auth_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    session['state'] = state
    return redirect(auth_url)

# def login():
#     auth_url, state = flow.authorization_url(access_type='offline',
#             include_granted_scopes='true',prompt='consent')
#     print(auth_url)
#     session['state'] = state
#     return redirect(auth_url)



@auth.route('/auth/callback')
def callback():
    """Handle the OAuth2 callback"""
    try:
        flow = create_flow()
        flow.fetch_token(authorization_response=request.url)
        credentials = flow.credentials

        session['credentials'] = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        }

        return redirect(url_for('views.homepage'))
    except Exception as e:
        print(f"Callback error: {e}")
        return str(e), 500
# def callback():
#     """Handle the OAuth2 callback"""
#     flow = create_flow()
#     flow.fetch_token(authorization_response=request.url)
#     credentials = flow.credentials
#
#     # Store credentials in session
#     session['credentials'] = {
#         'token': credentials.token,
#         'refresh_token': credentials.refresh_token,
#         'token_uri': credentials.token_uri,
#         'client_id': credentials.client_id,
#         'client_secret': credentials.client_secret,
#         'scopes': credentials.scopes
#     }
#
#     # Optionally store in token file for persistence
#     with open('token.json', 'w') as token:
#         token.write(credentials.to_json())
#
#     return redirect(url_for('views.homepage'))
# # def callback():
# #     flow.fetch_token(authorization_response=request.url)
# #     credentials = flow.credentials
# #     print(credentials)
# #     session['credentials'] = {
# #         'token': credentials.token,
# #         'refresh_token': credentials.refresh_token,
# #         'token_uri': credentials.token_uri,
# #         'client_id': credentials.client_id,
# #         'client_secret': credentials.client_secret,
# #         'scopes': credentials.scopes
# #     }
# #     print("EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE")
# #     return redirect(url_for('views.homepage'))

@auth.route('/raman.html', methods=['GET','POST'])
def book_appointment():
    if request.method == 'POST':
        action = request.form['action']
        if action == 'check_availability':
            day = request.form.get('day')
            time = request.form.get('time')
            print(type(day), type(time))
            avail = Appointment.scheduleAppointment(day, time)
            return render_template('raman.html', result=avail)
        elif action == 'submit_booking':
            book_id = request.form.get('selected_booking').upper()
            user_id = "Dummy_ID1"
            print(book_id, user_id)
            booking = Appointment.scheduleAppointments(book_id, user_id, action)
            return redirect(url_for('views.homepage'))

    result = '0'
    return render_template('raman.html',result = result)
